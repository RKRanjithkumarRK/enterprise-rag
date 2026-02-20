from pypdf import PdfReader
from pathlib import Path

def load_pdf(pdf_path: str) -> list[dict]:
    """load a pdf and return a list of documents with text and metadata
       Each document corresponds to one page
    """

    reader = PdfReader(pdf_path)
    documents = []

    for page_number, page in enumerate(reader.pages):
        text = page.extract_text()

        if text:
            documents.append({
                "text": text.strip(),
                "metadata": {
                    "source": Path(pdf_path).name,
                    "page": page_number + 1
                }
            })

    return documents
