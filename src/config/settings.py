"""
settings.py
-----------
Central config and environment variable loader for the RAG system.

Place this file at: src/config/settings.py

Why have a dedicated settings file?
  - Single place to manage ALL environment variables and config values.
  - Other modules import from here instead of scattering os.getenv() calls
    across every file — easier to maintain and audit.
  - Config values like TOP_K or CHUNK_MAX_CHARS can be tuned on cloud
    via environment variables without touching code.

NOTE: Gemini has been fully removed. This project uses Groq exclusively.
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==========================================
# LLM — Groq
# ==========================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found in environment variables. "
        "Add it to your .env file locally, or set it as an environment "
        "variable on Render / Streamlit Cloud."
    )


# ==========================================
# RAG Pipeline Config
# ==========================================

# How many chunks to retrieve from ChromaDB before reranking
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", 10))

# How many chunks to keep after reranking (final context sent to LLM)
TOP_K_RERANK = int(os.getenv("TOP_K_RERANK", 3))

# Maximum characters per text chunk during ingestion
CHUNK_MAX_CHARS = int(os.getenv("CHUNK_MAX_CHARS", 1200))


# ==========================================
# Hallucination Detection
# ==========================================

# Cosine similarity threshold — answers below this are flagged as ungrounded
GROUNDING_THRESHOLD = float(os.getenv("GROUNDING_THRESHOLD", 0.65))