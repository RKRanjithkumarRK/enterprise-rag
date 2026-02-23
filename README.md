---
title: Enterprise Policy RAG
emoji: 🔐
colorFrom: indigo
colorTo: green
sdk: docker
pinned: false
license: mit
---

# 🔐 Enterprise Policy RAG System

> Ask natural language questions about your enterprise policy documents — get grounded, cited, hallucination-resistant answers in seconds.

[![Live API](https://img.shields.io/badge/API-Live-brightgreen)](https://ranjith00743-enterprise-policy-rag.hf.space/docs)
[![Live UI](https://img.shields.io/badge/UI-Live-blue)](https://ranjith00743-enterprise-policy-ui.hf.space)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Overview

Enterprise policy documents are dense, long, and hard to navigate. Employees waste time searching through PDFs to find answers to simple compliance questions.

This system solves that with a **production-grade RAG (Retrieval-Augmented Generation) pipeline** that:

- Ingests any enterprise policy PDF automatically at startup
- Breaks it into semantically meaningful section-based chunks
- Embeds and stores them in a vector database for fast retrieval
- Retrieves the most relevant sections for any natural language query
- Generates a **grounded answer** using Groq LLM — strictly from document context, never from model memory
- Detects and flags potential hallucinations using cosine similarity scoring
- Returns structured JSON with the answer, source citations, and confidence scores

No prompt injection. No hallucinations. No guesswork.

---

## 🏗️ Architecture

```
                   ┌──────────────────────────────────────┐
                   │          INGESTION PIPELINE           │
                   │                                      │
 Policy PDF ──► PDF Loader ──► Text Cleaner ──► Section Chunker
                                                     │
                                              Embedder (MiniLM)
                                                     │
                                           ChromaDB (Vector Store)
                   └──────────────────────────────────────┘

                   ┌──────────────────────────────────────┐
                   │            QUERY PIPELINE             │
                   │                                      │
 User Query ──► Query Embedder ──► Retriever (Top-K)
                                         │
                                    Top 3 Chunks
                                         │
                               Groq LLM (Grounded Answer)
                                         │
                              Hallucination Detector
                                         │
                              Structured JSON Output
                   └──────────────────────────────────────┘
```

### Key Design Decisions

**Section-based chunking** — Rather than splitting text by fixed character count, the system detects numbered section headers (e.g., `3.1 Access Control`) and chunks by section boundaries. This preserves document structure and improves retrieval precision.

**In-memory ChromaDB with singleton pattern** — The vector store is initialized once at server startup and reused across all requests. This prevents re-embedding the entire PDF on every query — a critical performance optimization for cloud deployments.

**Grounded prompting** — The LLM is explicitly instructed to answer only from retrieved context chunks. If the answer isn't in the document, it says so. No creative inference allowed.

**Cosine similarity hallucination detection** — After generation, the answer embedding is compared against the retrieved context embedding. Answers scoring below 0.65 similarity are flagged as potentially ungrounded.

---

## 💼 Use Cases

**Compliance Q&A** — Employees can instantly ask "What are my data handling responsibilities?" instead of reading 40 pages of policy.

**Vendor & Third-Party Audits** — Quickly surface policy clauses related to vendor contracts, SLAs, and third-party access controls.

**Onboarding Automation** — New hires can query the policy document directly rather than scheduling meetings with HR or compliance teams.

**Policy Gap Analysis** — Teams can probe the document for specific topics and identify missing or weak policy sections based on what the system can't answer.

**Regulatory Readiness** — Legal and compliance teams can rapidly cross-reference internal policy against regulatory requirements by asking targeted questions.

---

## ⚙️ Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| LLM | Groq `llama-3.1-8b-instant` | Fast, grounded answer generation |
| Vector Store | ChromaDB (in-memory) | Semantic chunk storage and retrieval |
| Embeddings | `all-MiniLM-L6-v2` | Lightweight, accurate sentence embeddings |
| PDF Parsing | PyPDF | Extracts raw text from policy documents |
| API | FastAPI + Uvicorn | High-performance REST API with Swagger UI |
| Frontend | Streamlit | Interactive question-answer interface |
| Deployment (API) | Hugging Face Spaces (Docker) | Free, public, persistent API hosting |
| Deployment (UI) | Hugging Face Spaces (Docker) | Free, public Streamlit frontend |

---

## 📁 Project Structure

```
enterprise-rag/
├── src/
│   ├── api/                  # FastAPI app + lifespan ingestion
│   ├── answering/            # End-to-end RAG pipeline orchestrator
│   ├── chunking/             # Section-based + fallback text chunker
│   ├── cleaning/             # PDF noise removal and text normalization
│   ├── config/               # Centralized settings and env var loader
│   ├── embeddings/           # Chunk embedding with SentenceTransformers
│   ├── evaluation/           # Hallucination detector + system evaluator
│   ├── generation/           # Groq LLM grounded answer generation
│   ├── ingestion/            # PDF loader (PyPDF)
│   ├── llm/                  # Groq client wrapper
│   ├── reranking/            # Cross-encoder reranker (local use)
│   ├── retrieval/            # ChromaDB vector similarity retrieval
│   └── vectorstore/          # ChromaDB collection manager (singleton)
├── data/
│   └── raw_pdfs/             # Policy PDF goes here
├── streamlit_app.py          # Streamlit frontend
├── Dockerfile                # Docker config for HF Spaces (port 7860)
├── requirements.txt          # Pinned dependencies
└── .env                      # Local API keys (never committed)
```

---

## 🚀 Getting Started Locally

### 1. Clone the repository

```bash
git clone https://github.com/Ranjith00743/enterprise-rag.git
cd enterprise-rag
```

### 2. Install dependencies

```bash
pip install torch==2.2.2+cpu --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key at [console.groq.com](https://console.groq.com).

### 4. Add your PDF

Place your policy PDF at:
```
data/raw_pdfs/Information Security & Management Policy v3.pdf
```

### 5. Start the API

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8080 --reload
```

On first start, the system ingests the PDF automatically (~30–60 seconds). Subsequent requests use the cached vector store.

### 6. Test the API

```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the scope of this policy?"}'
```

### 7. Run the Streamlit frontend

```bash
BACKEND_URL=http://localhost:8080 streamlit run streamlit_app.py
```

---

## 🌐 Live Deployment

| Service | URL |
|---|---|
| 🔧 FastAPI (Backend) | https://ranjith00743-enterprise-policy-rag.hf.space |
| 📖 Swagger UI | https://ranjith00743-enterprise-policy-rag.hf.space/docs |
| 🎨 Streamlit (Frontend) | https://ranjith00743-enterprise-policy-ui.hf.space |

Both deployed on **Hugging Face Spaces** using Docker. The API runs on port 7860 with automatic PDF ingestion at startup.

---

## 📊 API Response Format

```json
{
  "answer": "The policy applies to all employees, contractors, and third-party vendors...",
  "sources": [
    { "section_number": "1", "section_title": "Scope" },
    { "section_number": "3.1", "section_title": "Plan (Establish the ISMS)" }
  ],
  "confidence_score": 0.75,
  "confidence_level": "Medium",
  "grounded_in_context": true,
  "grounding_similarity_score": 0.82
}
```

### Confidence Levels

| Score | Level | Meaning |
|---|---|---|
| ≥ 0.85 | High | Strong retrieval match |
| 0.65 – 0.84 | Medium | Good match, minor uncertainty |
| < 0.65 | Low | Weak retrieval, treat with caution |

---

## 🛡️ Anti-Hallucination Design

Two independent layers prevent fabricated answers:

**Layer 1 — Grounded prompting**: The LLM system prompt strictly forbids using outside knowledge. If the answer isn't in the retrieved chunks, the model responds with a standard fallback message rather than guessing.

**Layer 2 — Cosine similarity check**: After generation, the answer and retrieved context are both embedded and compared. A similarity score below 0.65 sets `grounded_in_context: false` in the response, giving the caller a signal to treat the answer with caution.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
