# 🤖 Acme Tech Solutions — RAG Chatbot Backend

A fully local Retrieval-Augmented Generation (RAG) chatbot backend built with **FastAPI**, **Pinecone**, **Ollama**, and **nomic-embed-text**. No OpenAI or paid AI API required.

---

## 📁 Project Structure

```
rag_chatbot/
├── docs/                    ← Source documents (ingest these into Pinecone)
│   ├── company_history.md
│   ├── products.md
│   └── hr_policy.md
├── routes/
│   ├── chat.py              ← POST /api/chat  (streaming response)
│   ├── ingest.py            ← POST /api/ingest
│   ├── history.py           ← GET  /api/history/{session_id}
│   └── session.py           ← DELETE /api/session/{session_id}
├── config.py                ← All settings (models, thresholds, chunk size)
├── embeddings.py            ← Ollama embedding calls
├── memory.py                ← Per-session conversation history
├── vectorstore.py           ← Pinecone + BM25 hybrid search
├── ingestion.py             ← Document chunking + ingestion pipeline
├── ingest_docs.py           ← One-shot script to load docs into Pinecone
├── main.py                  ← FastAPI app entry point
├── requirements.txt
├── .env                     ← Your secret keys (do NOT share this)
└── .env.example             ← Template for .env
```

---

## ✅ Prerequisites

Make sure the following are installed **before** you start:

| Tool | Where to get it | Check it works |
|---|---|---|
| **Python 3.10+** | [python.org](https://www.python.org/downloads/) | `python --version` |
| **Ollama** | [ollama.com](https://ollama.com/) | `ollama --version` |
| **Pinecone account** | [app.pinecone.io](https://app.pinecone.io/) (free tier) | — |

---

## 🚀 Step-by-Step Setup

### Step 1 — Pull the required Ollama models

Open a terminal and run:

```bash
ollama pull nomic-embed-text:latest
ollama pull llama3.2
```

> These models must be downloaded before running the app. `nomic-embed-text` handles embeddings and `llama3.2` handles generating answers.

---

### Step 2 — Create your Pinecone index

1. Log in to [app.pinecone.io](https://app.pinecone.io/)
2. Click **"Create Index"**
3. Use these exact settings:

   | Setting | Value |
   |---|---|
   | Index name | `priya-rag-index` |
   | **Dimensions** | **`768`** ← very important! |
   | Metric | `cosine` |
   | Plan | Serverless (free) |

> ⚠️ **Dimension must be 768** — this matches the `nomic-embed-text` model output size.

---

### Step 3 — Clone / open the project folder

```bash
cd c:\Users\Priya\OneDrive\Desktop\Final_project\rag_chatbot
```

---

### Step 4 — Set up the `.env` file

The `.env` file already exists with your Pinecone credentials. To verify it looks like this:

```
PINECONE_API_KEY=pcsk_4q8red_...
PINECONE_INDEX_NAME=priya-rag-index
```

If it doesn't exist, copy the template:

```bash
copy .env.example .env
# Then open .env and fill in your keys
```

---

### Step 5 — Install Python dependencies

```bash
pip install -r requirements.txt
```

This installs: `fastapi`, `uvicorn`, `pinecone-client`, `ollama`, `rank-bm25`, `python-dotenv`, `aiofiles`, `python-multipart`.

---

### Step 6 — Load the documents into Pinecone

```bash
python ingest_docs.py
```

Expected output:
```
Connecting to Pinecone …
→ Ingesting 'company_history.md' …
  ✓  2 chunk(s) stored
→ Ingesting 'products.md' …
  ✓  2 chunk(s) stored
→ Ingesting 'hr_policy.md' …
  ✓  2 chunk(s) stored

Done! 6 total chunk(s) in Pinecone.
```

> You only need to run this **once**. Re-running it is safe — it updates existing vectors instead of creating duplicates.

---

### Step 7 — Start the server

```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
[Startup] Connecting to Pinecone …
[Startup] Ready!
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## 🧪 Testing the API

### Interactive docs (easiest)
Open your browser: **http://localhost:8000/docs**

This gives you a full Swagger UI to test every endpoint with a form.

---

### Test with `curl`

**Ask a question:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What products does Acme offer?\", \"session_id\": \"test1\"}"
```

**Add a new document:**
```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Acme launched a new product called DataPilot in 2024.\", \"filename\": \"news.md\"}"
```

**Get chat history:**
```bash
curl http://localhost:8000/api/history/test1
```

**Delete a session:**
```bash
curl -X DELETE http://localhost:8000/api/session/test1
```

**Get all sessions (sidebar):**
```bash
curl http://localhost:8000/
```

---

## 📡 API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | List all chat sessions |
| `POST` | `/api/chat` | Send a message, get a streaming response |
| `POST` | `/api/ingest` | Ingest a document (JSON body) |
| `POST` | `/api/ingest/file` | Ingest a document (file upload) |
| `GET` | `/api/history/{session_id}` | Get full chat history for a session |
| `DELETE` | `/api/session/{session_id}` | Delete a session |

---

## 🔧 Tuning Settings (`config.py`)

| Setting | Default | What it does |
|---|---|---|
| `CHUNK_SIZE` | `512` words | How big each document chunk is |
| `CHUNK_OVERLAP` | `50` words | Words shared between consecutive chunks |
| `TOP_K` | `3` | Max chunks injected into the LLM prompt |
| `SIMILARITY_THRESHOLD` | `0.75` | Minimum score to use a chunk (lower = more results, more hallucination risk) |
| `MEMORY_WINDOW` | `3` | Last N message pairs sent to the LLM |
| `OLLAMA_TEMPERATURE` | `0.1` | LLM creativity (lower = more factual) |

---

## ❓ Troubleshooting

| Problem | Fix |
|---|---|
| `Connection refused` on Ollama | Make sure Ollama is running: open the Ollama app or run `ollama serve` |
| `Index not found` on Pinecone | Create the index first (Step 2) |
| `Dimension mismatch` error | Delete the Pinecone index and re-create it with **dimension = 768** |
| Empty responses / no context | Run `python ingest_docs.py` first to populate Pinecone |
| Port 8000 already in use | Use a different port: `uvicorn main:app --reload --port 8001` |
