# 🤖 RAG Chatbot — Acme Tech Solutions

A production-ready **Retrieval-Augmented Generation (RAG) Chatbot** built with:

- 🐍 **Backend** — FastAPI + LangChain + Pinecone (vector search) + SQLite (chat history) + Google Gemini
- ⚛️ **Frontend** — React 19 + Vite + Tailwind CSS

---

## 📁 Project Structure

```
RAG_Chatbot/
├── rag_chatbot/          # Python FastAPI backend
│   ├── routes/           # API route handlers (chat, history, session, ingest)
│   ├── middleware/       # Auth middleware
│   ├── docs/             # Source documents for RAG ingestion
│   ├── main.py           # FastAPI app entry point
│   ├── config.py         # Configuration (reads .env)
│   ├── vectorstore.py    # Pinecone vector store logic + local BM25 fallback
│   ├── embeddings.py     # Gemini embedding setup
│   ├── memory.py         # SQLite chat session management
│   ├── ingest_docs.py    # One-shot script to load docs into Pinecone
│   ├── requirements.txt  # Python dependencies
│   └── .env.example      # Backend env template
│
├── rag_frontend/         # React + Vite frontend
│   ├── src/
│   │   ├── components/   # ChatWindow, Sidebar, MessageBubble
│   │   ├── App.jsx       # Root component
│   │   ├── api.js        # Axios API calls to backend
│   │   └── index.css     # Global styles
│   ├── package.json
│   └── .env.example      # Frontend env template
│
├── .gitignore
└── README.md
```

---

## ✅ Prerequisites

Make sure you have the following installed:

| Tool | Version | Download |
|------|---------|----------|
| Python | ≥ 3.10 | [python.org](https://python.org) |
| Node.js | ≥ 18.x | [nodejs.org](https://nodejs.org) |
| Git | any | [git-scm.com](https://git-scm.com) |

You will also need accounts / API keys for:
- **Pinecone** — [pinecone.io](https://pinecone.io) (free tier works)
- **Google Gemini** — [aistudio.google.com](https://aistudio.google.com) (needs an API Key)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Priyap1038/ChatBot.git
cd ChatBot
```

---

### 2. Backend Setup (`rag_chatbot/`)

#### a) Create a virtual environment

```bash
cd rag_chatbot

# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

#### b) Install dependencies

```bash
pip install -r requirements.txt
```

#### c) Configure environment variables

```bash
# Copy the example file
copy .env.example .env        # Windows
cp .env.example .env          # macOS / Linux
```

Now open `.env` and fill in your values:

```env
GEMINI_API_KEY=AIzaSy...                # Your Gemini API key
PINECONE_API_KEY=pcsk_...              # Your Pinecone API key
PINECONE_INDEX_NAME=acme-chat-gemini-index    # Your Pinecone index name
CORS_ORIGINS=*                         # Use * for local dev
RATE_LIMIT=30/minute
LOG_LEVEL=INFO
```

#### d) Create Pinecone Index

> ⚠️ **CRITICAL**: Create your index in Pinecone with **Dimensions = 3072** and **Metric = cosine**. This matches the default Gemini `models/gemini-embedding-001` model output.

#### e) Ingest documents into Pinecone

> This step uploads your documents in `docs/` into the Pinecone vector store and builds the local BM25 search corpus (`bm25_corpus.json`).
> Run this **once** before starting the server (or whenever you physically add new files to `docs/`). The local search state survives restarts!

```bash
python ingest_docs.py
```

#### f) Start the backend server

```bash
uvicorn main:app --reload --port 8000
```

The API will be live at: **http://localhost:8000**

- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

---

### 3. Frontend Setup (`rag_frontend/`)

Open a **new terminal** and run:

#### a) Install Node dependencies

```bash
cd rag_frontend
npm install
```

#### b) Configure environment variables

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

For local development, the default `.env` values work out of the box (Vite proxies `/api/*` → `localhost:8000`):

```env
VITE_API_URL=       # Leave empty for local dev
VITE_API_KEY=       # Leave empty unless backend API_KEY is set
```

#### c) Start the frontend dev server

```bash
npm run dev
```

The app will be live at: **http://localhost:5173**

---

## 🖥️ Running Both Together (Quick Start)

Open **two terminals** side-by-side:

| Terminal 1 — Backend | Terminal 2 — Frontend |
|---|---|
| `cd rag_chatbot` | `cd rag_frontend` |
| `venv\Scripts\activate` | `npm install` |
| `uvicorn main:app --reload` | `npm run dev` |

Then open **http://localhost:5173** in your browser. 🎉

---

## 📄 Adding Your Own Documents

1. Place your `.md`, `.txt`, or `.pdf` files inside `rag_chatbot/docs/`
2. Re-run the ingestion script:
   ```bash
   cd rag_chatbot
   python ingest_docs.py
   ```
3. Restart the backend server.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/sessions` | List all chat sessions |
| `POST` | `/api/chat` | Send a message |
| `GET` | `/api/history/{session_id}` | Get chat history for a session |
| `POST` | `/api/session` | Create a new session |
| `POST` | `/api/ingest` | Ingest a document via API |

Full interactive docs: **http://localhost:8000/docs**

---

## 🏗️ Production Build (Frontend)

```bash
cd rag_frontend
npm run build
```

Output will be in `rag_frontend/dist/`. Serve it with any static host (Vercel, Netlify, etc.).

For the backend, update `.env`:
```env
CORS_ORIGINS=https://yourfrontend.com
API_KEY=your-strong-secret-key
```

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` | Make sure your venv is activated and `pip install -r requirements.txt` was run |
| Pinecone `Dimension mismatch` error | Delete the index and recreate it with **dimension = 1536** |
| Gemini API Error | Check your Gemini API key and quota |
| Empty responses / no context | Run `python ingest_docs.py` to populate Pinecone and the local database |
| CORS errors in browser | Ensure `CORS_ORIGINS=*` is set in backend `.env` during development |
| Frontend can't reach backend | Make sure backend is running on port `8000` and frontend on `5173` |

---

## 📜 License

This project is for educational / internal use. Feel free to fork and adapt!
