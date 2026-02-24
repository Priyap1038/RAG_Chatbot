# Acme Tech Solutions — RAG Chatbot Frontend

React + Vite frontend for the Acme Tech Solutions RAG chatbot. Streams real-time responses from the FastAPI backend via Server-Sent Events (SSE).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | React 18 |
| Build tool | Vite |
| Styling | Tailwind CSS |
| API | Fetch + SSE streaming |
| State | React `useState` + `localStorage` |

---

## Project Structure

```
rag_frontend/
├── src/
│   ├── components/
│   │   ├── Sidebar.jsx        # Session list, New Chat, document upload
│   │   ├── ChatWindow.jsx      # Message history + SSE streaming input
│   │   └── MessageBubble.jsx   # Individual message rendering
│   ├── App.jsx                 # Root — session state + localStorage
│   ├── api.js                  # All backend API calls
│   ├── main.jsx
│   └── index.css
├── .env.example                # Environment variable template
├── vite.config.js              # Dev proxy config
└── package.json
```

---

## Environment Variables

Copy `.env.example` to `.env` (development) or `.env.production` (production build):

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `` (empty) | Backend base URL. Empty = Vite proxy (dev). Set to `https://api.yourapp.com` in prod. |
| `VITE_API_KEY` | `` (empty) | Optional Bearer token if backend `API_KEY` is set. |

---

## Development

> **Requires the backend to be running on port 8000 first.**

```bash
# Install dependencies
npm install

# Start dev server (port 5173 or next available)
npm run dev
```

The Vite dev server proxies all `/api/*` requests to `http://localhost:8000` automatically — no CORS issues.

Open [http://localhost:5173](http://localhost:5173)

---

## Production Build

```bash
# Build optimised static files → dist/
npm run build

# Preview the production build locally
npm run preview
```

Deploy the `dist/` folder to any static host (Vercel, Netlify, nginx, S3, etc.).

For production, set `VITE_API_URL` in `.env.production` to your backend URL:
```
VITE_API_URL=https://api.yourapp.com
```

---

## Features

- **Real-time streaming** — responses appear token-by-token as the LLM generates them
- **Session management** — create, switch, and delete chat sessions from the sidebar
- **Session persistence** — active session and messages restored after page refresh (localStorage)
- **Document upload** — upload `.md` / `.txt` files directly from the sidebar
- **Provider-agnostic** — works with Ollama (local) and Google Gemini backends via a single config switch

---

## Switching the Backend Provider

No frontend changes needed. Change `LLM_PROVIDER` in `rag_chatbot/config.py`:

```python
LLM_PROVIDER = "ollama"   # ← dev / no API key
LLM_PROVIDER = "gemini"   # ← production / with GEMINI_API_KEY
```

---

## API Endpoints Used

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/sessions` | List all sessions |
| `POST` | `/api/session` | Register new session |
| `DELETE` | `/api/session/:id` | Delete session |
| `GET` | `/api/history/:id` | Fetch message history |
| `POST` | `/api/chat` | Send message (SSE stream) |
| `POST` | `/api/ingest/file` | Upload document |
| `GET` | `/api/health` | Backend health check |
