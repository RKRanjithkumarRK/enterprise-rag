from src.cleaning.text_cleaner import clean_text

def clean_documents(documents):
    cleaned_docs = []

    for doc in documents:
        cleaned_docs.append({
            "text": clean_text(doc["text"]),
            "metadata": doc["metadata"]
        })

    return cleaned_docs