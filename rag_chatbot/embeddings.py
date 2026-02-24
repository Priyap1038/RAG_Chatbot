# embeddings.py
# ─────────────────────────────────────────────────────
# LANGCHAIN INTEGRATION: uses LangChain OpenAIEmbeddings.
# ─────────────────────────────────────────────────────

from config import EMBEDDING_MODEL, GEMINI_API_KEY

_cache: dict[str, list[float]] = {}

from langchain_google_genai import GoogleGenerativeAIEmbeddings
_embedder = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    google_api_key=GEMINI_API_KEY,
)

def get_embedding(text: str) -> list[float]:
    """
    Embed a single text string using the active LangChain embedder.
    Result is cached so identical text is never re-embedded.
    """
    if text in _cache:
        return _cache[text]

    clean = text.replace("\n", " ").strip()
    vector = _embedder.embed_query(clean)

    _cache[text] = vector
    return vector

def get_embedder():
    """Return the shared LangChain embedder instance (used by PineconeVectorStore)."""
    return _embedder
