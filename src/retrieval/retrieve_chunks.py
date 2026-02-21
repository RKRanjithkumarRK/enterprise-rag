from sentence_transformers import SentenceTransformer

def retrieve_chunks(collection, query, top_k=5):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results