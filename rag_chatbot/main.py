# main.py  —  FastAPI application entry point (production-ready)
# ─────────────────────────────────────────────────────

import logging
import logging.config

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from routes.chat    import router as chat_router
from routes.ingest  import router as ingest_router
from routes.history import router as history_router
from routes.session import router as session_router
from middleware.auth import APIKeyMiddleware
from vectorstore import init_pinecone
from memory import init_db, get_all_sessions
from config import CORS_ORIGINS, RATE_LIMIT, LOG_LEVEL

# ── Structured logging ────────────────────────────────
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Rate limiter (slowapi) ────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])

# ── FastAPI app ───────────────────────────────────────
app = FastAPI(
    title="Acme Tech Solutions RAG Chatbot",
    description="Production-ready RAG chatbot powered by LangChain + Pinecone.",
    version="2.0.0",
    docs_url="/docs",      # Swagger UI — disable in prod if needed
    redoc_url="/redoc",
)

# ── Middleware (order matters: outermost first) ───────

# 1. Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,     # from env — "*" in dev, locked in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Optional Bearer token auth
app.add_middleware(APIKeyMiddleware)

# ── Routers ───────────────────────────────────────────
app.include_router(chat_router)
app.include_router(ingest_router)
app.include_router(history_router)
app.include_router(session_router)


# ── Startup ───────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    logger.info("=== Acme RAG Chatbot starting up ===")
    logger.info("Initialising SQLite database …")
    init_db()
    logger.info("Connecting to Pinecone …")
    init_pinecone()
    logger.info("=== Startup complete — ready to serve ===")


# ── Health check ──────────────────────────────────────
# @app.get("/")
# async def root():
#     return {"message": "Welcome to the Acme RAG Chatbot API"}

@app.get("/api/health", tags=["ops"])
async def health():
    """Liveness probe — always returns 200 if the server is up."""
    return {"status": "ok", "version": "2.0.0"}


# ── Sessions list ─────────────────────────────────────
@app.get("/", include_in_schema=False)
async def home():
    sessions = get_all_sessions()
    return {"sessions": sessions, "total": len(sessions)}


@app.get("/api/sessions", tags=["sessions"])
async def list_sessions():
    """Return all chat sessions for the sidebar."""
    sessions = get_all_sessions()
    return {"sessions": sessions, "total": len(sessions)}
