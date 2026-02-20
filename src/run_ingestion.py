"""
run_ingestion.py
----------------
Full ingestion pipeline: PDF → clean → chunk → embed → store in ChromaDB.
"""

import os
from dotenv import load_dotenv
from src.ingestion.pdf_loader import load_pdf
from src.cleaning.clean_documents import clean_documents
from src.chunking.apply_chunking import chunk_clean_documents
from src.embeddings.embed_chunks import embed_chunks
from src.vectorstore.chroma_store import create_chroma_collection
from src.vectorstore.store_chunks import store_chunks


def run_ingestion():
    """
    Runs the full document ingestion pipeline and stores chunks in ChromaDB.
    Called automatically by answer_query.py if the vector store is empty.
    """

    load_dotenv()

    # ── Absolute path fix ──────────────────────────────────────────────────────
    # __file__ is always the absolute path to THIS file (run_ingestion.py).
    # We go one level up (to src/) then one more level up (to project root)
    # to build a path that works regardless of where the server is launched from.
    # This is the single most important fix for cloud deployment reliability.
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_path = os.path.join(
        BASE_DIR,
        "data",
        "raw_pdfs",
        "Information Security & Management Policy v3.pdf"
    )

    # Safety check — give a clear human-readable error if the PDF is missing
    # rather than a cryptic FileNotFoundError deep in the traceback.
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"PDF not found at: {pdf_path}\n"
            f"Please make sure the file exists at data/raw_pdfs/ in your project root."
        )

    print("\n==============================")
    print("STEP 1: Loading PDF")
    print("==============================\n")

    raw_docs = load_pdf(pdf_path)
    print(f"Pages loaded: {len(raw_docs)}")

    print("\n==============================")
    print("STEP 2: Removing Noisy Pages")
    print("==============================\n")

    filtered_docs = [doc for doc in raw_docs if doc["metadata"]["page"] > 2]
    print(f"Pages after filtering: {len(filtered_docs)}")

    print("\n==============================")
    print("STEP 3: Cleaning Pages")
    print("==============================\n")

    clean_docs = clean_documents(filtered_docs)

    print("\n==============================")
    print("STEP 4: Merging Pages")
    print("==============================\n")

    merged_text = "\n\n".join(doc["text"] for doc in clean_docs)
    merged_doc = [{
        "text": merged_text,
        "metadata": {"source": clean_docs[0]["metadata"]["source"]}
    }]

    print("\n==============================")
    print("STEP 5: Section-Based Chunking")
    print("==============================\n")

    chunks = chunk_clean_documents(merged_doc)
    print(f"Total chunks created: {len(chunks)}\n")

    print("\n==============================")
    print("STEP 6: Generating Embeddings")
    print("==============================\n")

    embeddings = embed_chunks(chunks)
    print(f"Embedding shape: {embeddings.shape}")

    print("\n==============================")
    print("STEP 7: Storing in ChromaDB")
    print("==============================\n")

    collection = create_chroma_collection()
    store_chunks(collection, chunks, embeddings)

    print(f"Ingestion complete. {len(chunks)} chunks stored in ChromaDB.")
    return collection


if __name__ == "__main__":
    from src.retrieval.retrieve_chunks import retrieve_chunks
    from src.reranking.rerank_chunks import rerank_chunks

    collection = run_ingestion()

    print("\n==============================")
    print("STEP 8: Testing Retrieval")
    print("==============================\n")

    query = "What is the scope of this policy?"
    results = retrieve_chunks(collection, query, top_k=10)
    retrieved_docs = results["documents"][0]
    retrieved_metadata = results["metadatas"][0]

    reranked_docs, reranked_metadata, confidence_score = rerank_chunks(
        query, retrieved_docs, retrieved_metadata, top_k=3
    )

    for i, doc in enumerate(reranked_docs):
        print(f"--- Result {i+1} ---")
        print(doc[:700])
        print("Metadata:", reranked_metadata[i])
        print()