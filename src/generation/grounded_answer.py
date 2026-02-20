"""
grounded_answer.py
------------------
Generates a grounded answer using Groq LLM.

Place this file at: src/answering/grounded_answer.py

"Grounded" means the model is strictly instructed to answer ONLY from
the retrieved context chunks — this is the core anti-hallucination
mechanism in the RAG pipeline.

Pipeline position:
    retrieve_chunks → rerank_chunks → [this file] → hallucination_detector
"""

from src.llm.groq_client import get_groq_client, GROQ_MODEL


def generate_grounded_answer(query: str, retrieved_chunks: list) -> str:
    """
    Given a user query and a list of retrieved text chunks,
    generates a grounded answer using Groq.

    Args:
        query           : The user's question as plain text.
        retrieved_chunks: List of strings — the top-k retrieved chunks
                          from ChromaDB after retrieval and reranking.

    Returns:
        A plain text answer string from the LLM.
    """

    client = get_groq_client()

    # Combine all retrieved chunks into one context block.
    # We use a clear separator (---) between chunks so the model
    # understands these are distinct sections of the source document,
    # not one continuous piece of text.
    context_text = "\n\n---\n\n".join(retrieved_chunks)

    prompt = f"""You are an Information Security Policy Assistant.

Your ONLY job is to answer the user's question using the context below.
Do NOT use any outside knowledge. Do NOT make up information.

If the answer is not found in the context, respond with exactly:
"The answer is not available in the provided document."

Context:
{context_text}

Question:
{query}

Answer:"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict, grounded policy assistant. "
                    "Answer only from the provided context. Never invent information."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,  # 0 = fully deterministic — no creativity, only facts
    )

    return response.choices[0].message.content.strip()