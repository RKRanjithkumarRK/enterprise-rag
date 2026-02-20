"""
run_ingestion.py
----------------
Full ingestion pipeline: PDF → clean → chunk → embed → store in ChromaDB.

Place this file at: project root (same level as requirements.txt)

WHY this is wrapped in a function and not just a script:
    answer_query.py does this:

        from run_ingestion import run_ingestion
        run_ingestion()

    If ALL the code were at module level (not inside a function), Python
    would execute everything the moment that import line runs — before
    run_ingestion() is even called. That means your server would try to
    load the PDF just by importing this file. Wrapping it in a function
    prevents that — it only runs when explicitly called.

    The if __name__ == "__main__" block at the bottom is the "developer
    mode switch" — it only activates when you run this file directly:
        python run_ingestion.py
    It does NOT activate when the file is imported.
"""

import os
from dotenv import load_dotenv
from src.ingestion.pdf_loader import load_pdf
from src.cleaning.clean_documents import clean_documents
from src.chunking.apply_chunking import chunk_clean_documents
from src.embeddings.embed_chunks import embed_chunks
from src.vectorstore.chroma_store import create_chroma_collection
from src.vectorstore.store_chunks import store_chunks


# ==========================================
# MAIN INGESTION FUNCTION
# ==========================================

def run_ingestion():
    """
    Runs the full document ingestion pipeline and stores chunks in ChromaDB.

    Called automatically by answer_query.py if the vector store is empty.
    Also callable directly via:  python run_ingestion.py

    Returns:
        collection: The populated ChromaDB collection object, so the caller
                    (answer_query.py) can reuse it immediately without
                    creating a new empty collection right after ingestion.
    """

    load_dotenv()

    print("\n==============================")
    print("STEP 1: Loading PDF")
    print("==============================\n")

    pdf_path = "data/raw_pdfs/Information Security & Management Policy v3.pdf"

    raw_docs = load_pdf(pdf_path)
    print(f"Pages loaded: {len(raw_docs)}")


    print("\n==============================")
    print("STEP 2: Removing Noisy Pages")
    print("==============================\n")

    # Remove the first 2 pages (cover page, table of contents, etc.)
    # These pages contain repeated headers and no useful policy content.
    filtered_docs = [
        doc for doc in raw_docs
        if doc["metadata"]["page"] > 2
    ]

    print(f"Pages after filtering: {len(filtered_docs)}")


    print("\n==============================")
    print("STEP 3: Cleaning Pages")
    print("==============================\n")

    clean_docs = clean_documents(filtered_docs)


    print("\n==============================")
    print("STEP 4: Merging Pages")
    print("==============================\n")

    # We merge all pages into a single document BEFORE section-based chunking.
    # Why? Because section headers often span page boundaries in PDFs.
    # If we chunked page-by-page, we'd split sections in the middle and
    # lose the structural context that the section_chunker relies on.
    merged_text = "\n\n".join(doc["text"] for doc in clean_docs)

    merged_doc = [{
        "text": merged_text,
        "metadata": {
            "source": clean_docs[0]["metadata"]["source"]
        }
    }]


    print("\n==============================")
    print("STEP 5: Section-Based Chunking")
    print("==============================\n")

    chunks = chunk_clean_documents(merged_doc)

    print(f"Total section-based chunks created: {len(chunks)}\n")

    # Preview the first 3 chunks so you can visually verify
    # that the section detection is working correctly.
    for i in range(min(3, len(chunks))):
        print(f"\n========== CHUNK {i+1} ==========\n")
        print("Section Number:", chunks[i]["metadata"].get("section_number"))
        print("Section Title:", chunks[i]["metadata"].get("section_title"))
        print("\nContent Preview:\n")
        print(chunks[i]["text"][:800])
        print("\n----------------------------------------\n")


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

    # Return the collection so answer_query.py can reuse it directly
    # rather than calling create_chroma_collection() again (which would
    # give it back the same singleton, but this makes the intent explicit).
    return collection


# ==========================================
# DIRECT EXECUTION — developer testing only
# ==========================================

if __name__ == "__main__":
    """
    Runs when you execute:  python run_ingestion.py
    Does NOT run when this file is imported by answer_query.py.

    Step 8 lives here because it's a developer sanity-check tool —
    it verifies that retrieval and reranking work after ingestion.
    It's not part of the production pipeline.
    """

    # These imports are only needed for the Step 8 test,
    # so we keep them here rather than at the top of the file.
    from src.retrieval.retrieve_chunks import retrieve_chunks
    from src.reranking.rerank_chunks import rerank_chunks

    # Run the full ingestion pipeline first
    collection = run_ingestion()


    print("\n==============================")
    print("STEP 8: Testing Retrieval + Reranking")
    print("==============================\n")

    query = "What is the scope of this policy?"

    results = retrieve_chunks(collection, query, top_k=10)

    retrieved_docs = results["documents"][0]
    retrieved_metadata = results["metadatas"][0]

    reranked_docs, reranked_metadata, confidence_score = rerank_chunks(
        query,
        retrieved_docs,
        retrieved_metadata,
        top_k=3
    )

    print("\nReranked Results:\n")

    for i, doc in enumerate(reranked_docs):
        print(f"--- Result {i+1} ---")
        print(doc[:700])
        print("Metadata:", reranked_metadata[i])
        print()