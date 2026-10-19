
from pathlib import Path

import chromadb
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# Project paths
BASE_DIR = Path(__file__).resolve().parents[1]
CHROMA_DIR = BASE_DIR / "data" / "chroma"

# FastAPI application
app = FastAPI(title="AI Tech Consultant - Knowledge Brain")

# Local vector database
client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_or_create_collection(name="support_articles")

# Local embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Preliminary threshold: evaluate using test questions
MAX_DISTANCE = 0.65


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "Knowledge Brain is running in free mode."
    }


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
            "needs_human": False
        }

    if collection.count() == 0:
        return {
            "answer": (
                "The knowledge base is empty. "
                "Please ask a human support specialist."
            ),
            "sources": [],
            "needs_human": True
        }

    # Convert the question into an embedding
    embedding = model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    # Search for relevant support evidence
    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(5, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    documents = results.get("documents", [[]])[0] or []
    metadatas = results.get("metadatas", [[]])[0] or []
    distances = results.get("distances", [[]])[0] or []

    # Keep only evidence that passes the preliminary threshold
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
            "distance": distance
        })

    if not relevant:
        return {
            "answer": (
                "I could not find sufficiently relevant evidence "
                "in the support articles. Please ask a human "
                "support specialist."
            ),
            "sources": [],
            "needs_human": True
        }

    # Combine evidence from the same article
    grouped_sources = {}

    for item in relevant:
        url = item["url"] or item["title"]

        if url not in grouped_sources:
            grouped_sources[url] = {
                "title": item["title"],
                "url": item["url"],
                "evidence_parts": []
            }

        if item["evidence"] not in grouped_sources[url]["evidence_parts"]:
            grouped_sources[url]["evidence_parts"].append(
                item["evidence"]
            )

    sources = []

    for item in grouped_sources.values():
        evidence = " ".join(item["evidence_parts"])

        sources.append({
            "title": item["title"],
            "url": item["url"],
            "evidence": evidence[:1000]
        })

    # This is evidence formatting, not an AI-generated answer
    answer = (
        "I found potentially relevant information in the "
        "support knowledge base. Review the evidence and "
        "source links below. This free mode does not generate "
        "a Claude-written answer, so please verify the steps "
        "against the cited support article."
    )

    return {
        "answer": answer,
        "sources": sources,
        "needs_human": False
    }
