from src.chunking.section_chunker import section_chunk_text


def split_long_text(text, max_chars=1200):
    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chars

        if end < len(text):
            last_period = text.rfind(".", start, end)
            if last_period != -1:
                end = last_period + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end

    return chunks


def chunk_clean_documents(documents):

    all_chunks = []
    global_chunk_id = 0

    for doc in documents:
        text = doc["text"]
        metadata = doc["metadata"]

        sections = section_chunk_text(text)

        for section in sections:
            sub_chunks = split_long_text(section["text"])

            for sub_text in sub_chunks:
                all_chunks.append({
                    "text": sub_text,
                    "metadata": {
                        "chunk_id": global_chunk_id,
                        "source": metadata.get("source"),
                        "section_number": section.get("section_number"),
                        "section_title": section.get("section_title")
                    }
                })

                global_chunk_id += 1

    return all_chunks
