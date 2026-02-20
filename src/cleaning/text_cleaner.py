import re

def clean_text(text: str) -> str:

    # Remove standalone page numbers
    text = re.sub(r"(?m)^\s*\d+\s*$", "", text)

    # Remove footer/header repeating patterns
    text = re.sub(
        r"INFORMATION\s+SECURITY\s+&\s+MANAGEMENT\s+POLICY\s*\d*",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Fix broken spaced words like IN FO RMATIO N
    text = re.sub(r"([A-Z])\s+(?=[A-Z])", r"\1", text)

    # Normalize excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove duplicate paragraphs
    paragraphs = text.split("\n")

    unique_paragraphs = []
    seen = set()

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if para not in seen:
            unique_paragraphs.append(para)
            seen.add(para)

    return "\n".join(unique_paragraphs)
