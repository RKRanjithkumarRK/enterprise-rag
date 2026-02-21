from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from src.answering.answer_query import answer_query
import traceback

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run ingestion ONCE at startup, not on every request
    print("Running ingestion at startup...")
    from src.run_ingestion import run_ingestion
    run_ingestion()
    print("Ingestion complete. Server ready.")
    yield

app = FastAPI(
    title="Enterprise Policy RAG API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def root():
    return {"status": "RAG API is running"}

@app.post("/ask")
def ask_question(request: QueryRequest):
    try:
        result = answer_query(request.question)
        return result
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}