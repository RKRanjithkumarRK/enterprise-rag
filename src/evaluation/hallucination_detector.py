from sentence_transformers import SentenceTransformer, util
import torch


# Lightweight embedding model for semantic comparison
grounding_model = SentenceTransformer("all-MiniLM-L6-v2")


def detect_hallucination(answer, context_chunks, threshold=0.65):
    """
    Checks whether the generated answer is grounded in context.

    Returns:
        - grounded (True/False)
        - similarity_score (float)
    """

    if not answer.strip():
        return False, 0.0

    # Combine context into one text block
    context_text = " ".join(context_chunks)

    # Embed both answer and context
    answer_embedding = grounding_model.encode(answer, convert_to_tensor=True)
    context_embedding = grounding_model.encode(context_text, convert_to_tensor=True)

    # Compute cosine similarity
    similarity = util.cos_sim(answer_embedding, context_embedding)

    score = similarity.item()

    grounded = score >= threshold

    return grounded, round(score, 3)
