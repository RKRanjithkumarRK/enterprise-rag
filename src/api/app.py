"""
app.py
------
FastAPI application with full Swagger support, CORS middleware,
structured response models, and proper error handling.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import traceback

from src.answering.answer_query import answer_query

app = FastAPI(
    title="Enterprise Policy RAG API",
    description="""
A production-grade Retrieval-Augmented Generation (RAG) system for querying 
enterprise policy documents. Ask questions in plain English and get grounded, 
cited answers with confidence scores and hallucination detection.
    """,
    version="1.0.0",
    docs_url="/docs",       # Swagger UI lives here
    redoc_url="/redoc"      # ReDoc alternative UI lives here
)

# CORS middleware is essential for Swagger's "Try it out" button to work.
# Without this, the browser blocks the request from /docs to your API
# because they appear to come from different origins — a security feature
# of all modern browsers called CORS (Cross-Origin Resource Sharing).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Schema ─────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str

    class Config:
        # This pre-fills the Swagger UI request body so testers
        # immediately know what format to use — no guesswork needed.
        json_schema_extra = {
            "example": {
                "question": "What is the scope of this policy?"
            }
        }


# ── Response Schemas ───────────────────────────────────────────────────────────
# Without these explicit models, Swagger has no schema to display
# and the response section shows nothing useful after you click Execute.
class SourceItem(BaseModel):
    section_number: Optional[str] = None
    section_title: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    confidence_score: float
    confidence_level: str
    grounded_in_context: bool
    grounding_similarity_score: float


# ── Health Check ───────────────────────────────────────────────────────────────
@app.get("/", summary="Health Check", tags=["Status"])
def root():
    """Confirms the API server is live and accepting requests."""
    return {"status": "RAG API is running"}


# ── Main Endpoint ──────────────────────────────────────────────────────────────
@app.post(
    "/ask",
    response_model=QueryResponse,
    summary="Ask a Policy Question",
    tags=["RAG Pipeline"]
)
def ask_question(request: QueryRequest):
    """
    Submit a natural language question about the enterprise policy document.

    The system retrieves the most relevant sections, generates a grounded
    answer using Groq LLM, runs hallucination detection, and returns
    everything with source citations and a confidence score.
    """
    try:
        result = answer_query(request.question)
        return result

    except Exception as e:
        # Capture the full Python traceback and send it back in the
        # HTTP error response — this is what makes debugging possible.
        # Instead of a blank "Internal Server Error", you'll see the
        # exact file, line number, and error message that caused the crash.
        error_detail = traceback.format_exc()
        print("ERROR in /ask endpoint:\n", error_detail)
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline error: {str(e)}\n\nTraceback:\n{error_detail}"
        )