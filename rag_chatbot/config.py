# config.py  —  All application settings (production-ready)
# ─────────────────────────────────────────────────────
import os
from dotenv import load_dotenv

load_dotenv()

# ── OpenAI ────────────────────────────────────────────
OPENAI_API_KEY: str        = os.getenv("OPENAI_API_KEY", "")
OPENAI_CHAT_MODEL: str     = "gpt-3.5-turbo"
OPENAI_EMBED_MODEL: str    = "text-embedding-3-small"
OPENAI_EMBED_DIM: int      = 1536
OPENAI_TEMPERATURE: float  = 0.0

# ── Active settings ────────────────────────────────────
EMBEDDING_MODEL     = OPENAI_EMBED_MODEL
EMBEDDING_DIMENSION = OPENAI_EMBED_DIM
CHAT_TEMPERATURE    = OPENAI_TEMPERATURE

# ── Pinecone ──────────────────────────────────────────
PINECONE_API_KEY: str    = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "priya-rag-index")

# ── Persistence paths ─────────────────────────────────
_BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
# Note: Using absolute path ensures we don't accidentally create files in CWD
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
API_KEY: str = os.getenv("API_KEY", "")

CORS_ORIGINS: list[str] = [
    o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")
]

# ── Logging ───────────────────────────────────────────
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# ── Rate limiting ─────────────────────────────────────
RATE_LIMIT: str = os.getenv("RATE_LIMIT", "30/minute")
