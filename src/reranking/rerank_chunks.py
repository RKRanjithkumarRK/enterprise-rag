from sentence_transformers import CrossEncoder
import math

# Load once globally (important for performance)
reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def sigmoid(x):
    """
    Convert raw cross-encoder score into 0-1 confidence scale.
    """
    return 1 / (1 + math.exp(-x))


def rerank_chunks(query, retrieved_docs, retrieved_metadata, top_k=3):
    """
    Rerank retrieved documents using cross-encoder scoring.

    Returns:
        top_docs: list[str]
        top_metadata: list[dict]
        confidence_score: float (0-1)
    """

    # 🛑 Safety: No retrieval results
    if not retrieved_docs:
        return [], [], 0.0

    # Prepare (query, document) pairs
    pairs = [(query, doc) for doc in retrieved_docs]

    # Get raw relevance scores
    scores = reranker_model.predict(pairs)

    # Combine docs + metadata + scores
    scored_docs = list(zip(retrieved_docs, retrieved_metadata, scores))

    # Sort descending by score
    scored_docs.sort(key=lambda x: x[2], reverse=True)

    # Select top_k
    top_results = scored_docs[:top_k]

    top_docs = [item[0] for item in top_results]
    top_metadata = [item[1] for item in top_results]

    # Confidence calculation
    # Use highest score → normalize with sigmoid
    highest_score = top_results[0][2]
    confidence_score = sigmoid(highest_score)

    return top_docs, top_metadata, confidence_score
