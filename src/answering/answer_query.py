"""
answer_query.py
---------------
Full RAG pipeline orchestrator. Coordinates retrieval, generation,
hallucination detection, and structured output formatting.
"""

import json
from src.vectorstore.chroma_store import create_chroma_collection
from src.retrieval.retrieve_chunks import retrieve_chunks
from src.generation.grounded_answer import generate_grounded_answer
from src.evaluation.hallucination_detector import detect_hallucination


def classify_confidence(score):
    """Converts a raw float score into a human-readable confidence label."""
    if score >= 0.85:
        return "High"
    elif score >= 0.65:
        return "Medium"
    else:
        return "Low"


def answer_query(query, top_k=10):
    """
    End-to-end RAG pipeline.

    Args:
        query  : The user's question as a plain string.
        top_k  : How many chunks to retrieve from ChromaDB before selecting top 3.

    Returns:
        A structured dict with the answer, sources, confidence, and grounding info.
    """

    # ── Step 1: Load ChromaDB collection ──────────────────────────────────────
    collection = create_chroma_collection()

    # If the collection is empty (cold start), trigger ingestion.
    # The import lives INSIDE the if-block intentionally — we only need
    # run_ingestion when the collection is empty, not on every request.
    if collection.count() == 0:
        from src.run_ingestion import run_ingestion   # FIXED: full package path
        run_ingestion()

    # ── Step 2: Retrieve relevant chunks ──────────────────────────────────────
    retrieval_results = retrieve_chunks(collection, query, top_k=top_k)
    retrieved_docs = retrieval_results["documents"][0]
    retrieved_metadata = retrieval_results["metadatas"][0]

    if not retrieved_docs:
        return {
            "answer": "No relevant content found.",
            "sources": [],
            "confidence_score": 0,
            "confidence_level": "Low",
            "grounded_in_context": False,
            "grounding_similarity_score": 0
        }

    # ── Step 3: Take top 3 chunks ──────────────────────────────────────────────
    reranked_docs = retrieved_docs[:3]
    reranked_metadata = retrieved_metadata[:3]
    confidence_score = 0.75

    # ── Step 4: Generate grounded answer ──────────────────────────────────────
    answer = generate_grounded_answer(query, reranked_docs)

    # ── Step 5: Hallucination detection ───────────────────────────────────────
    grounded, grounding_score = detect_hallucination(answer, reranked_docs)

    # ── Step 6: Deduplicate sources ───────────────────────────────────────────
    unique_sources = []
    seen = set()

    for meta in reranked_metadata:
        key = (meta.get("section_number"), meta.get("section_title"))
        if key not in seen:
            seen.add(key)
            unique_sources.append({
                "section_number": meta.get("section_number"),
                "section_title": meta.get("section_title")
            })

    # ── Step 7: Return structured output ──────────────────────────────────────
    return {
        "answer": answer,
        "sources": unique_sources,
        "confidence_score": round(confidence_score, 2),
        "confidence_level": classify_confidence(confidence_score),
        "grounded_in_context": grounded,
        "grounding_similarity_score": grounding_score
    }


if __name__ == "__main__":
    user_query = input("Enter your question: ")
    result = answer_query(user_query)
    print("\n==============================")
    print("STRUCTURED ENTERPRISE OUTPUT")
    print("==============================\n")
    print(json.dumps(result, indent=4))