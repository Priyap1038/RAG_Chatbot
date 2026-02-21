# config.py  —  All application settings (production-ready)
# ─────────────────────────────────────────────────────
import os
from dotenv import load_dotenv

load_dotenv()

# ══════════════════════════════════════════════════════
# 🔀  PROVIDER SWITCH  (one line)
# ══════════════════════════════════════════════════════
LLM_PROVIDER = "ollama"   # "ollama" or "openai"

# ── OpenAI ────────────────────────────────────────────
OPENAI_API_KEY: str        = os.getenv("OPENAI_API_KEY", "")
OPENAI_CHAT_MODEL: str     = "gpt-3.5-turbo"
OPENAI_EMBED_MODEL: str    = "text-embedding-3-small"
OPENAI_EMBED_DIM: int      = 1536
OPENAI_TEMPERATURE: float  = 0.0

# ── Ollama ────────────────────────────────────────────
OLLAMA_CHAT_MODEL: str     = "llama3.2:1b"
OLLAMA_EMBED_MODEL: str    = "nomic-embed-text:latest"
OLLAMA_EMBED_DIM: int      = 768
OLLAMA_TEMPERATURE: float  = 0.1

# ── Active settings (auto-selected) ──────────────────
if LLM_PROVIDER == "openai":
    EMBEDDING_MODEL     = OPENAI_EMBED_MODEL
    EMBEDDING_DIMENSION = OPENAI_EMBED_DIM
    CHAT_TEMPERATURE    = OPENAI_TEMPERATURE
else:
    EMBEDDING_MODEL     = OLLAMA_EMBED_MODEL
    EMBEDDING_DIMENSION = OLLAMA_EMBED_DIM
    CHAT_TEMPERATURE    = OLLAMA_TEMPERATURE

# ── Pinecone ──────────────────────────────────────────
PINECONE_API_KEY: str    = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "priya-rag-index")

# ── Persistence paths ─────────────────────────────────
_BASE_DIR    = os.path.dirname(__file__)
DB_PATH: str     = os.getenv("DB_PATH",     os.path.join(_BASE_DIR, "sessions.db"))
CORPUS_PATH: str = os.getenv("CORPUS_PATH", os.path.join(_BASE_DIR, "bm25_corpus.json"))

# ── Chunking ──────────────────────────────────────────
CHUNK_SIZE: int    = 1200
CHUNK_OVERLAP: int = 150

# ── Retrieval ─────────────────────────────────────────
TOP_K: int                  = 2
SIMILARITY_THRESHOLD: float = 0.55

# ── Memory ────────────────────────────────────────────
MEMORY_WINDOW: int = 3

# ── Security ──────────────────────────────────────────
# If set, all /api/* requests must include:
#   Authorization: Bearer <API_KEY>
# Leave blank to disable auth (development mode).
API_KEY: str = os.getenv("API_KEY", "")

# Comma-separated list of allowed CORS origins.
# Example: "https://myapp.com,https://www.myapp.com"
# Use "*" only in development.
CORS_ORIGINS: list[str] = [
    o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")
]

# ── Logging ───────────────────────────────────────────
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# ── Rate limiting ─────────────────────────────────────
RATE_LIMIT: str = os.getenv("RATE_LIMIT", "30/minute")
