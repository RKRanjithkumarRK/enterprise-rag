# 🔐 Enterprise Policy RAG System

A production-grade **Retrieval-Augmented Generation (RAG)** system that lets you ask natural language questions about enterprise policy documents and get grounded, cited answers — powered by **Groq LLM**, **ChromaDB**, and **Sentence Transformers**.

---

## 🧠 What It Does

Instead of manually searching through a dense policy PDF, you simply ask a question like:

> *"What is the scope of this policy?"*
> *"How are third-party vendors managed?"*

The system retrieves the most relevant sections from the document, passes them to an LLM, and returns a **grounded answer with source citations and a confidence score** — no hallucinations, no guesswork.

---

## 🏗️ System Architecture

```
PDF Document
     ↓
PDF Loader → Text Cleaner → Section Chunker → Embedder
                                                   ↓
                                             ChromaDB (Vector Store)
                                                   ↓
User Query → Query Embedder → Retriever → Top-K Chunks
                                               ↓
                                        Groq LLM (Grounded Answer)
                                               ↓
                                    Hallucination Detector → Final Output
```

---

## ⚙️ Tech Stack

| Component | Tool |
|---|---|
| LLM | Groq (`llama-3.1-8b-instant`) |
| Vector Store | ChromaDB (in-memory) |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Deployment | Render (API) / Streamlit Cloud (UI) |

---

## 📁 Project Structure

```
enterprise-rag/
├── src/
│   ├── api/              # FastAPI app
│   ├── answering/        # RAG pipeline orchestrator
│   ├── chunking/         # Section-based text chunker
│   ├── cleaning/         # Text cleaning utilities
│   ├── config/           # Settings and environment variables
│   ├── embeddings/       # Chunk embedding logic
│   ├── evaluation/       # Hallucination detection + system eval
│   ├── generation/       # Groq LLM answer generation
│   ├── ingestion/        # PDF loader
│   ├── llm/              # Groq client
│   ├── reranking/        # Cross-encoder reranker
│   ├── retrieval/        # ChromaDB retrieval
│   └── vectorstore/      # ChromaDB collection manager
├── data/
│   └── raw_pdfs/         # Place your policy PDF here
├── streamlit_app.py      # Streamlit frontend
├── render.yaml           # Render deployment config
├── requirements.txt
└── .env                  # Your API keys (never committed)
```

---

## 🚀 Getting Started Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/enterprise-rag.git
cd enterprise-rag
```

### 2. Install dependencies

```bash
pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### 3. Set up your environment variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key at [console.groq.com](https://console.groq.com).

### 4. Add your PDF

Place your policy PDF inside `data/raw_pdfs/` and update the path in `src/run_ingestion.py` if needed.

### 5. Start the API server

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 10000 --reload
```

On first start, the system will automatically ingest the PDF, chunk it, embed it, and store it in ChromaDB. This takes about 30–60 seconds.

### 6. Test the API

```bash
curl -X POST http://localhost:10000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the scope of this policy?"}'
```

### 7. Run the Streamlit frontend (optional)

```bash
streamlit run streamlit_app.py
```

---

## 🌐 Deploying to Render

1. Push this repo to GitHub.
2. Go to [render.com](https://render.com) → New Web Service → Connect your repo.
3. Render will auto-detect `render.yaml` and configure the service.
4. In the Render dashboard, add your environment variable:
   - `GROQ_API_KEY` = your actual key
5. Deploy — done!

---

## 📊 API Response Format

```json
{
  "answer": "The policy applies to all employees and third-party vendors...",
  "sources": [
    { "section_number": "1", "section_title": "Scope" }
  ],
  "confidence_score": 0.75,
  "confidence_level": "Medium",
  "grounded_in_context": true,
  "grounding_similarity_score": 0.82
}
```

---

## 🛡️ Anti-Hallucination Design

The system uses two layers to prevent hallucinated answers:

**Grounded prompting** — the LLM is strictly instructed to answer only from the retrieved context chunks, never from its own training knowledge.

**Cosine similarity check** — after generation, the answer is embedded and compared against the retrieved context. If the similarity score falls below 0.65, the answer is flagged as ungrounded in the response.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
