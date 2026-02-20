# test_env.py
# -----------
# Sanity check to confirm GROQ_API_KEY is loading correctly from .env
# Run with: python src/test_env.py

from src.config.settings import GROQ_API_KEY

print("Groq key loaded successfully:", GROQ_API_KEY[:10], "...")
