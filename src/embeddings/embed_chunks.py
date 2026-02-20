from sentence_transformers import SentenceTransformer

# Load the model ONCE at module level — not inside the function.
# On a cloud server with limited RAM (512MB on free tier), reloading
# a 90MB model repeatedly is the fastest way to get an out-of-memory crash.
model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_chunks(chunks):
    """
    Convert text chunks to vector embeddings using the pre-loaded model.
    The model is shared across all calls — no redundant loading.
    """
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings