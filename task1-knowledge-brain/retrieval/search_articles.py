
import chromadb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
CHROMA_DIR = BASE_DIR / "data" / "chroma"

COLLECTION_NAME = "support_articles"
TOP_K = 3
MAX_DISTANCE = 0.65


def main():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    if collection.count() == 0:
        print("Knowledge base is empty. Index articles first.")
        return

    question = input("\nAsk a support question: ").strip()

    if not question:
        print("Please enter a question.")
        return

    results = collection.query(
        query_texts=[question],
        n_results=min(TOP_K, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0] or []
    metadatas = results.get("metadatas", [[]])[0] or []
    distances = results.get("distances", [[]])[0] or []

    if not documents or not distances:
        print("No evidence found. Please ask a human support specialist.")
        return

    print("\n--- Knowledge Brain Search Results ---")

    if distances[0] > MAX_DISTANCE:
        print("No sufficiently relevant evidence found.")
        print("Please ask a human support specialist.")
        print(f"Best distance: {distances[0]:.4f}")
        return

    found_relevant = False

    for number, (document, metadata, distance) in enumerate(
        zip(documents, metadatas, distances),
        start=1,
    ):
        if distance > MAX_DISTANCE:
            continue

        found_relevant = True
        print(f"\nResult {number}")
        print("Title:", metadata.get("title", "Unknown"))
        print("Source:", metadata.get("url", "Unknown"))
        print(f"Distance: {distance:.4f}")
        print("Evidence:", document[:500])

    if not found_relevant:
        print("No sufficiently relevant evidence found.")
        print("Please ask a human support specialist.")
        return

    print("\nReview the evidence before answering the customer.")
    print("This script retrieves evidence; it does not generate an AI answer.")


if __name__ == "__main__":
    main()
