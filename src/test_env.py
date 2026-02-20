# test_env.py
# -----------
# Quick sanity check to confirm your GROQ_API_KEY is loading correctly
# from the .env file. Run this directly: python src/test_env.py

from src.config.settings import GROQ_API_KEY

print("Groq key loaded:", GROQ_API_KEY[:10], "...")