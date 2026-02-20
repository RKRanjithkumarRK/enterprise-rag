"""
groq_client.py
--------------
Centralized Groq LLM client.

Place this file at: src/llm/groq_client.py
Also create an empty src/llm/__init__.py so Python treats it as a package.

Why centralize it here?
  - One place to change the model or API key logic.
  - Every other module just calls get_groq_client() and stays clean.
  - Swapping to a different Groq model (e.g. llama-3.3-70b) = change ONE line.
"""

import os
from groq import Groq
from dotenv import load_dotenv

# Load .env for local development.
# On cloud (Render / Streamlit Cloud), env vars are injected by the platform directly.
load_dotenv()

# ---- Change this one line to switch models across the entire project ----
GROQ_MODEL = "llama-3.1-8b-instant"


def get_groq_client():
    """
    Returns a configured Groq client instance.
    Raises a clear, human-readable error if the API key is missing.
    """
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. "
            "Add it to your .env file locally, or set it as an "
            "environment variable on Render / Streamlit Cloud."
        )

    return Groq(api_key=api_key)