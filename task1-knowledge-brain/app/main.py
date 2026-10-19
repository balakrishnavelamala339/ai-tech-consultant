
from pathlib import Path

import chromadb
from fastapi import FastAPI
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parents[1]
CHROMA_DIR = BASE_DIR / "data" / "chroma"

app = FastAPI(title="AI Tech Consultant - Knowledge Brain")

client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_or_create_collection(
    name="support_articles",
    metadata={"hnsw:space": "cosine"},
)

MAX_DISTANCE = 0.65


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "Knowledge Brain is running in free mode."}


@app.get("/health")
def health_check():
    return {"status": "healthy", "mode": "free"}


@app.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        return {
            "answer": "Please enter a question.",
            "sources": [],
            "needs_human": False,
        }

    count = collection.count()

    if count == 0:
        return {
            "answer": (
                "The knowledge base is empty. "
                "Please ask a human support specialist."
            ),
            "sources": [],
            "needs_human": True,
        }

    results = collection.query(
        query_texts=[question],
        n_results=min(5, count),
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0] or []
    metadatas = results.get("metadatas", [[]])[0] or []
    distances = results.get("distances", [[]])[0] or []

    relevant = []

    for document, metadata, distance in zip(
        documents, metadatas, distances
    ):
        if not document or distance > MAX_DISTANCE:
            continue

        relevant.append({
            "title": metadata.get("title", "Unknown"),
            "url": metadata.get("url", ""),
            "evidence": document.strip(),
        })

    if not relevant:
        return {
            "answer": (
                "I could not find sufficiently relevant evidence "
                "in the support articles. Please ask a human "
                "support specialist."
            ),
            "sources": [],
            "needs_human": True,
        }

    grouped_sources = {}

    for item in relevant:
        key = item["url"] or item["title"]

        if key not in grouped_sources:
            grouped_sources[key] = {
                "title": item["title"],
                "url": item["url"],
                "evidence_parts": [],
            }

        if item["evidence"] not in grouped_sources[key]["evidence_parts"]:
            grouped_sources[key]["evidence_parts"].append(item["evidence"])

    sources = []

    for item in grouped_sources.values():
        sources.append({
            "title": item["title"],
            "url": item["url"],
            "evidence": " ".join(item["evidence_parts"])[:1000],
        })

    answer = (
        "I found potentially relevant information in the support "
        "knowledge base. Review the evidence and source links below. "
        "This free mode does not generate a Claude-written answer, "
        "so please verify the steps against the cited support article."
    )

    return {
        "answer": answer,
        "sources": sources,
        "needs_human": False,
    }
