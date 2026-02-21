from sentence_transformers import SentenceTransformer
import gc

def embed_chunks(chunks):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=8)
    del model
    gc.collect()
    return embeddings