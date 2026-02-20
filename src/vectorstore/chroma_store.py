"""
chroma_store.py
---------------
ChromaDB client and collection manager.

Place this file at: src/vectorstore/chroma_store.py

KEY DESIGN DECISION — Global Singleton Pattern:
    Without this pattern, every call to answer_query() would call
    create_chroma_collection(), which would create a brand new empty
    in-memory collection. This means:

        Request 1 → collection created, ingestion runs, 50 chunks stored
        Request 2 → NEW collection created (empty!), ingestion runs AGAIN

    That would be catastrophically slow — re-embedding the entire PDF
    on every single user request.

    The singleton (_collection stored as a module-level variable) means:
        Request 1 → collection created, ingestion runs, 50 chunks stored
        Request 2 → existing collection returned immediately, no ingestion

    The collection lives in memory for the entire lifetime of the server
    process — exactly what we want on free-tier cloud hosting where there
    is no persistent disk.
"""

import chromadb


# Module-level variables — persist for the lifetime of the server process.
# This is intentional: it's the singleton that prevents repeated ingestion.
_client = None
_collection = None


def create_chroma_collection():
    """
    Returns the ChromaDB collection, creating it if it doesn't exist yet.

    Uses a module-level singleton so the same in-memory collection is
    reused across all calls within the same server process.

    Why in-memory (no persist_directory)?
        Free-tier hosting platforms (Render, Streamlit Cloud) have
        ephemeral filesystems — any file written to disk is wiped on
        restart. Persisting to disk would give a false sense of durability.
        In-memory + re-ingest-on-startup is more honest and equally fast
        for a single-document RAG system like this one.
    """
    global _client, _collection

    # If the collection already exists in memory, return it immediately.
    # This is the key line that prevents repeated ingestion.
    if _collection is not None:
        return _collection

    # First time this is called — create the client and collection.
    _client = chromadb.Client()  # Pure in-memory, no persistence

    _collection = _client.get_or_create_collection(
        name="policy_collection"
    )

    return _collection