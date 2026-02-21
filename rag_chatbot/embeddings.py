# embeddings.py
# ─────────────────────────────────────────────────────
# LANGCHAIN INTEGRATION: uses LangChain embedding wrappers for both providers.
#
#   "ollama"  → OllamaEmbeddings  (langchain_ollama)  — no API key needed
#   "openai"  → OpenAIEmbeddings  (langchain_openai)  — needs OPENAI_API_KEY
#
# No changes needed here when switching providers.
# ─────────────────────────────────────────────────────

from config import LLM_PROVIDER, EMBEDDING_MODEL, OPENAI_API_KEY

# In-memory cache to avoid re-embedding identical text
_cache: dict[str, list[float]] = {}

# LANGCHAIN INTEGRATION: build the correct embedder once at startup
if LLM_PROVIDER == "openai":
    # LANGCHAIN INTEGRATION: replaces direct openai client embeddings call
    from langchain_openai import OpenAIEmbeddings
    _embedder = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY,
    )
else:
    # LANGCHAIN INTEGRATION: replaces direct ollama.embeddings() call
    from langchain_ollama import OllamaEmbeddings
    _embedder = OllamaEmbeddings(model=EMBEDDING_MODEL)


def get_embedding(text: str) -> list[float]:
    """
    Embed a single text string using the active LangChain embedder.
    Result is cached so identical text is never re-embedded.
    """
    if text in _cache:
        return _cache[text]

    clean = text.replace("\n", " ").strip()

    # LANGCHAIN INTEGRATION: unified embed_query() API works for both providers
    vector = _embedder.embed_query(clean)

    _cache[text] = vector
    return vector


def get_embedder():
    """Return the shared LangChain embedder instance (used by PineconeVectorStore)."""
    return _embedder
