def paragraph_chunk_text(
    text: str,
    max_chunk_chars: int = 1200,
    overlap_paragraphs: int = 1
):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    current_chunk = []
    current_length = 0

    for para in paragraphs:
        para_length = len(para)

        if current_length + para_length > max_chunk_chars and current_chunk:
            chunks.append("\n\n".join(current_chunk))

            if overlap_paragraphs > 0:
                current_chunk = current_chunk[-overlap_paragraphs:]
                current_length = sum(len(p) for p in current_chunk)
            else:
                current_chunk = []
                current_length = 0

        current_chunk.append(para)
        current_length += para_length

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks
