
import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parents[1]
ARTICLES_FILE = BASE_DIR / "data" / "articles.jsonl"
CHROMA_DIR = BASE_DIR / "data" / "chroma"

# Local embedding model: no API key needed for embeddings.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150


def split_text(text):
    text = " ".join(text.split())
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunks.append(text[start:end])

        if end == len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def main():
    if not ARTICLES_FILE.exists():
        print("Articles file not found. Run the crawler first.")
        return

    articles = []
    for line in ARTICLES_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            articles.append(json.loads(line))

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name="support_articles",
        metadata={"hnsw:space": "cosine"},
    )

    model = SentenceTransformer(MODEL_NAME)
    documents, ids, metadatas = [], [], []

    for article in articles:
        chunks = split_text(article.get("text", ""))
        for number, chunk in enumerate(chunks):
            if not chunk.strip():
                continue

            # Stable IDs prevent duplicate chunks on repeated indexing.
            chunk_id = f"{article['url']}::chunk-{number}"
            documents.append(chunk)
            ids.append(chunk_id)
            metadatas.append({
                "url": article["url"],
                "title": article.get("title", ""),
                "chunk_number": number,
                "content_hash": article.get("content_hash", ""),
            })

    if not documents:
        print("No usable article text found. Check the crawler output.")
        return

    # Upsert makes repeated runs update the same chunk IDs.
    batch_size = 64
    for start in range(0, len(documents), batch_size):
        batch_docs = documents[start:start + batch_size]
        batch_ids = ids[start:start + batch_size]
        batch_meta = metadatas[start:start + batch_size]

        embeddings = model.encode(
            batch_docs,
            normalize_embeddings=True,
        ).tolist()

        collection.upsert(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_meta,
            embeddings=embeddings,
        )

    print(f"Indexed {len(articles)} articles.")
    print(f"Stored {len(documents)} searchable chunks.")
    print(f"Chroma database: {CHROMA_DIR}")


if __name__ == "__main__":
    main()
