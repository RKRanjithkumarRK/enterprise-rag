from fastapi import FastAPI
from pydantic import BaseModel
from src.answering.answer_query import answer_query

app = FastAPI(
    title="Enterprise Policy RAG API",
    description="Production-grade grounded Q&A system",
    version="1.0.0"
)


# =========================
# Request Schema
# =========================

class QueryRequest(BaseModel):
    question: str


# =========================
# Health Check
# =========================

@app.get("/")
def root():
    return {"status": "RAG API is running"}


# =========================
# Main Endpoint
# =========================

@app.post("/ask")
def ask_question(request: QueryRequest):
    result = answer_query(request.question)
    return result
