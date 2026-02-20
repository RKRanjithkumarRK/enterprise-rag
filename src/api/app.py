# src/api/app.py
# --------------
# FastAPI app with proper Swagger support, CORS middleware,
# and structured response models so the /docs UI renders correctly.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from src.answering.answer_query import answer_query

app = FastAPI(
    title="Enterprise Policy RAG API",
    description="""
    A production-grade Retrieval-Augmented Generation system for querying 
    enterprise policy documents. Ask questions in plain English and get 
    grounded, cited answers with confidence scores.
    """,
    version="1.0.0",
    # These two lines make Swagger work properly even on cloud deployments
    docs_url="/docs",
    redoc_url="/redoc"
)

# ── CORS Middleware ────────────────────────────────────────────────────────────
# This is essential for Swagger UI to make API calls from the browser.
# Without it, the browser blocks requests from the /docs page to your API
# because they appear to come from a "different origin".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Allow all origins (fine for a public API)
    allow_credentials=True,
    allow_methods=["*"],      # Allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)


# ── Request Schema ─────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str

    # This shows an example in the Swagger UI so testers know what to type
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the scope of this policy?"
            }
        }


# ── Response Schemas ───────────────────────────────────────────────────────────
# Defining these explicitly is what makes Swagger show the full response
# structure in the UI. Without them, Swagger just shows a blank response.

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
    """Check if the API is live and running."""
    return {"status": "RAG API is running"}


# ── Main Endpoint ──────────────────────────────────────────────────────────────
@app.post(
    "/ask",
    response_model=QueryResponse,   # This is the key line for Swagger to work!
    summary="Ask a Policy Question",
    tags=["RAG Pipeline"]
)
def ask_question(request: QueryRequest):
    """
    Submit a natural language question about the policy document.
    
    The system will retrieve relevant sections, generate a grounded answer,
    and return it with source citations and a confidence score.
    """
    result = answer_query(request.question)
    return result