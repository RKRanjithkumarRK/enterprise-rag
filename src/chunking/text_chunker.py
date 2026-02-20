def simple_chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    """Split text into overlapping chunks based on character count."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap

    return chunks

def chunk_documents(documents, chunk_size=1000, overlap=200):
    all_chunks = []

    for doc in documents:
        text = doc["text"]
        metadata = doc["metadata"]

        chunks = simple_chunk_text(text, chunk_size, overlap)

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "metadata":{
                    **metadata,
                    "chunk_id": i
                }
            })

    return all_chunks