# 🤖 RAG Chatbot — Acme Tech Solutions

A production-ready **Retrieval-Augmented Generation (RAG) Chatbot** built with:

- 🐍 **Backend** — FastAPI + LangChain + Pinecone (vector search) + SQLite (chat history)
- ⚛️ **Frontend** — React 19 + Vite + Tailwind CSS

---

## 📁 Project Structure

```
RAG_Chatbot/
├── rag_chatbot/          # Python FastAPI backend
│   ├── routes/           # API route handlers (chat, history, session, ingest)
│   ├── middleware/        # Auth middleware
│   ├── docs/             # Source documents for RAG ingestion
│   ├── main.py           # FastAPI app entry point
│   ├── config.py         # Configuration (reads .env)
│   ├── vectorstore.py    # Pinecone vector store logic
│   ├── embeddings.py     # Embedding model setup
│   ├── memory.py         # SQLite chat session management
│   ├── ingestion.py      # Document ingestion pipeline
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
- **OpenAI** (optional) — [platform.openai.com](https://platform.openai.com) *(or use Ollama locally)*

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
OPENAI_API_KEY=sk-...                   # Your OpenAI API key (if using OpenAI)
PINECONE_API_KEY=pcsk_...              # Your Pinecone API key
PINECONE_INDEX_NAME=priya-rag-index    # Your Pinecone index name
CORS_ORIGINS=*                         # Use * for local dev
RATE_LIMIT=30/minute
LOG_LEVEL=INFO
```

#### d) Ingest documents into Pinecone

> This step uploads your documents in `docs/` into the Pinecone vector store.
> Run this **once** before starting the server (or whenever you add new docs).

```bash
python ingest_docs.py
```

#### e) Start the backend server

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
| Pinecone connection error | Double-check `PINECONE_API_KEY` and `PINECONE_INDEX_NAME` in `.env` |
| CORS errors in browser | Ensure `CORS_ORIGINS=*` is set in backend `.env` during development |
| Frontend can't reach backend | Make sure backend is running on port `8000` and frontend on `5173` |
| Port already in use | Use `--port 8001` flag: `uvicorn main:app --reload --port 8001` |

---

## 📜 License

This project is for educational / internal use. Feel free to fork and adapt!
