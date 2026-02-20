"""
answer_query.py
---------------
Full RAG pipeline orchestrator.

This file's ONLY job is to coordinate all the moving parts:
    1. Load the ChromaDB collection (ingest if empty)
    2. Retrieve relevant chunks
    3. Generate a grounded answer  ← delegates to generation/grounded_answer.py
    4. Detect hallucination
    5. Format and return structured output

Notice there is NO Groq or LLM code here anymore.
That responsibility has been moved to generation/grounded_answer.py.
This separation means if you ever swap LLMs (e.g. Groq → OpenAI),
you only change one file — not this one.
"""

import json
from src.vectorstore.chroma_store import create_chroma_collection
from src.retrieval.retrieve_chunks import retrieve_chunks
from src.generation.grounded_answer import generate_grounded_answer
from src.evaluation.hallucination_detector import detect_hallucination


# ==========================================
# CONFIDENCE CLASSIFIER
# ==========================================

def classify_confidence(score):
    """
    Converts a raw float score into a human-readable confidence label.
    These thresholds are tunable — adjust based on your evaluation results.
    """
    if score >= 0.85:
        return "High"
    elif score >= 0.65:
        return "Medium"
    else:
        return "Low"


# ==========================================
# MAIN PIPELINE
# ==========================================

def answer_query(query, top_k=10):
    """
    End-to-end RAG pipeline.

    Args:
        query  : The user's question as a plain string.
        top_k  : How many chunks to retrieve from ChromaDB before reranking.

    Returns:
        A structured dict with the answer, sources, confidence, and grounding info.
    """

    # ── Step 1: Load ChromaDB collection ──────────────────────────────────────
    # create_chroma_collection() is a singleton — it returns the same in-memory
    # collection on every call instead of creating a new empty one each time.
    collection = create_chroma_collection()

    # If the collection is empty (e.g. cold start on a cloud server),
    # run the full ingestion pipeline to populate it before we do anything.
    if collection.count() == 0:
        from run_ingestion import run_ingestion
        run_ingestion()

    # ── Step 2: Retrieve relevant chunks ──────────────────────────────────────
    retrieval_results = retrieve_chunks(collection, query, top_k=top_k)

    retrieved_docs = retrieval_results["documents"][0]
    retrieved_metadata = retrieval_results["metadatas"][0]

    # Safety check — if retrieval came back empty, return a clean fallback.
    if not retrieved_docs:
        return {
            "answer": "No relevant content found.",
            "sources": [],
            "confidence_score": 0,
            "confidence_level": "Low",
            "grounded_in_context": False,
            "grounding_similarity_score": 0
        }

    # ── Step 3: Use top 3 chunks (reranking skipped for cloud deployment) ─────
    # Cross-encoder reranking is accurate but slow and memory-heavy.
    # On free-tier cloud (Render / Streamlit Cloud), we skip it and just
    # take the top 3 retrieved chunks. Confidence is fixed at 0.75 for now.
    # To re-enable reranking locally: from src.reranking.rerank_chunks import rerank_chunks
    reranked_docs = retrieved_docs[:3]
    reranked_metadata = retrieved_metadata[:3]
    confidence_score = 0.75

    # ── Step 4: Generate grounded answer ──────────────────────────────────────
    # This is the ONLY line that talks to the LLM.
    # All prompt building and Groq API logic lives in generation/grounded_answer.py.
    answer = generate_grounded_answer(query, reranked_docs)

    # ── Step 5: Hallucination detection ───────────────────────────────────────
    # Checks whether the generated answer is semantically grounded in the
    # retrieved context using cosine similarity between their embeddings.
    grounded, grounding_score = detect_hallucination(answer, reranked_docs)

    # ── Step 6: Deduplicate sources ───────────────────────────────────────────
    # Multiple chunks can come from the same section, so we deduplicate
    # by (section_number, section_title) before returning to the user.
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


# ==========================================
# CLI ENTRY POINT
# ==========================================

if __name__ == "__main__":
    """
    Run this file directly to test the full pipeline from the terminal:
        python -m src.answering.answer_query
    """
    user_query = input("Enter your question: ")
    result = answer_query(user_query)

    print("\n==============================")
    print("STRUCTURED ENTERPRISE OUTPUT")
    print("==============================\n")

    print(json.dumps(result, indent=4))