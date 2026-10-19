import asyncio
import hashlib
import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

SITEMAP_URL = (
    "https://support.brilliantdirectories.com/support/sitemap.xml"
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
MANIFEST_PATH = DATA_DIR / "manifest.json"
ARTICLES_PATH = DATA_DIR / "articles.jsonl"

# Start small. Increase this only after checking the results.
MAX_PAGES = 10
REQUEST_DELAY_SECONDS = 1.5
MAX_ATTEMPTS = 3
USER_AGENT = "AITechConsultantStudentBot/1.0"


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            print(f"Could not read {path}; starting with defaults.")
    return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".tmp")
    temp_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    temp_path.replace(path)


def get_sitemap_urls(xml_text):
    root = ET.fromstring(xml_text)
    urls = []

    for element in root.iter():
        if element.tag.split("}")[-1] == "loc" and element.text:
            urls.append(element.text.strip())

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(urls))


def extract_article(html, url):
    soup = BeautifulSoup(html, "html.parser")

    for element in soup.select(
        "script, style, nav, footer, header, noscript"
    ):
        element.decompose()

    main = soup.find("main") or soup.find("article") or soup.body or soup
    title_tag = soup.find("h1") or soup.title
    title = title_tag.get_text(" ", strip=True) if title_tag else url

    text = main.get_text("\n", strip=True)
    images = []

    for img in main.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src:
            images.append({
                "url": httpx.URL(url).join(src).__str__(),
                "alt": img.get("alt", ""),
            })

    return {
        "url": url,
        "title": title,
        "text": text,
        "images": images,
        "content_hash": hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def robots_allows(url):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    try:
        response = httpx.get(
            robots_url,
            headers={"User-Agent": USER_AGENT},
            timeout=15,
            follow_redirects=True,
        )
        if response.status_code == 404:
            return True

        response.raise_for_status()
        parser = RobotFileParser()
        parser.set_url(robots_url)
        parser.parse(response.text.splitlines())
        return parser.can_fetch(USER_AGENT, url)
    except httpx.HTTPError as exc:
        print(f"Could not check robots.txt: {exc}")
        return False


async def fetch_with_retries(client, url):
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            # Retry temporary server errors, not permanent client errors.
            if status < 500 or attempt == MAX_ATTEMPTS:
                print(f"Failed ({status}): {url}")
                return None
        except httpx.HTTPError as exc:
            if attempt == MAX_ATTEMPTS:
                print(f"Network error for {url}: {exc}")
                return None

        await asyncio.sleep(2 ** attempt)

    return None


async def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_json(MANIFEST_PATH, {})
    article_records = {}

    if ARTICLES_PATH.exists():
        for line in ARTICLES_PATH.read_text(
            encoding="utf-8"
        ).splitlines():
            try:
                item = json.loads(line)
                article_records[item["url"]] = item
            except (json.JSONDecodeError, KeyError):
                continue

    headers = {"User-Agent": USER_AGENT}

    async with httpx.AsyncClient(
        headers=headers,
        timeout=30,
        follow_redirects=True,
    ) as client:
        sitemap_text = await fetch_with_retries(client, SITEMAP_URL)
        if not sitemap_text:
            print("Could not download sitemap. Stopping safely.")
            return

        urls = get_sitemap_urls(sitemap_text)
        urls = [
            url for url in urls
            if urlparse(url).scheme == "https"
            and urlparse(url).netloc == "support.brilliantdirectories.com"
            and urlparse(url).path != "/support/sitemap.xml"
        ]

        # Some sitemaps are sitemap indexes containing other sitemaps.
        # Handle one level of nested sitemap files.
        nested = [
            url for url in urls
            if urlparse(url).path.endswith(".xml")
        ]
        for sitemap_url in nested:
            nested_text = await fetch_with_retries(client, sitemap_url)
            if nested_text:
                try:
                    urls.extend(get_sitemap_urls(nested_text))
                except ET.ParseError:
                    print(f"Invalid nested sitemap: {sitemap_url}")

        urls = list(dict.fromkeys(
            url for url in urls
            if urlparse(url).scheme == "https"
            and urlparse(url).netloc == "support.brilliantdirectories.com"
            and not urlparse(url).path.endswith(".xml")
        ))

        print(f"Found {len(urls)} candidate article URLs.")

        # Keep the first version small while we verify the crawler.
        selected_urls = urls[:MAX_PAGES]
        successful = 0

        for index, url in enumerate(selected_urls, start=1):
            if not robots_allows(url):
                manifest[url] = {
                    "status": "skipped_robots_or_policy_check_failed",
                    "checked_at": datetime.now(timezone.utc).isoformat(),
                }
                print(f"[{index}/{len(selected_urls)}] Skipped: {url}")
                continue

            previous = manifest.get(url, {})
            print(f"[{index}/{len(selected_urls)}] Fetching {url}")

            await asyncio.sleep(REQUEST_DELAY_SECONDS)
            html = await fetch_with_retries(client, url)

            if html is None:
                manifest[url] = {
                    "status": "failed",
                    "attempts": MAX_ATTEMPTS,
                    "last_attempt": datetime.now(timezone.utc).isoformat(),
                }
                save_json(MANIFEST_PATH, manifest)
                continue

            article = extract_article(html, url)
            old_hash = previous.get("content_hash")

            if old_hash == article["content_hash"]:
                manifest[url] = {
                    **previous,
                    "status": "unchanged",
                    "last_checked": article["fetched_at"],
                }
            else:
                article_records[url] = article
                manifest[url] = {
                    "status": "success",
                    "content_hash": article["content_hash"],
                    "last_checked": article["fetched_at"],
                }
                successful += 1

            # Save progress after each page so a restart can resume.
            ARTICLES_PATH.write_text(
                "".join(
                    json.dumps(item, ensure_ascii=False) + "\n"
                    for item in article_records.values()
                ),
                encoding="utf-8",
            )
            save_json(MANIFEST_PATH, manifest)

    print(f"Finished. Newly saved or updated pages: {successful}")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"Articles: {ARTICLES_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
