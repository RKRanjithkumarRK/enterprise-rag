import re

def section_chunk_text(text: str):
    """
    Splits text into section-based chunks using numbered headers.
    Supports:
        1. Title
        2 Title
        3.1 Title
        5.10 Title
    """

    pattern = r"(?m)^\s*(\d+(?:\.\d+)*)\.?\s+([A-Z][^\n]+)"

    matches = list(re.finditer(pattern, text))
    sections = []

    for i, match in enumerate(matches):
        section_number = match.group(1).strip()
        section_title = match.group(2).strip()

        start = match.start()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        section_text = text[start:end].strip()

        sections.append({
            "text": section_text,
            "section_number": section_number,
            "section_title": section_title
        })

    return sections
