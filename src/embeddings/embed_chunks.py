from sentence_transformers import SentenceTransformer

def embed_chunks(chunks):
    """
    Convert text chunks to vector embeddings
    """

    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    return embeddings