# vectorstore.py  —  Pinecone + BM25 hybrid search (production-ready)
# ─────────────────────────────────────────────────────
# PRODUCTION CHANGES:
#   1. BM25 corpus is persisted to a JSON file (CORPUS_PATH) so keyword
#      search survives server restarts without re-ingesting documents.
#   2. print() replaced with structured logging.
#   3. semantic_search uses LangChain PineconeVectorStore wrapper.
# ─────────────────────────────────────────────────────

import json
import logging
import os

from pinecone import Pinecone, ServerlessSpec
from rank_bm25 import BM25Okapi
from langchain_pinecone import PineconeVectorStore

from config import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    EMBEDDING_DIMENSION,
    CORPUS_PATH,
    TOP_K,
    SIMILARITY_THRESHOLD,
)

logger = logging.getLogger(__name__)

# ── Pinecone client ───────────────────────────────────
_pc         = Pinecone(api_key=PINECONE_API_KEY)
_index      = None
_vectorstore: PineconeVectorStore | None = None

# ── BM25 state ────────────────────────────────────────
_all_chunks: list[dict] = []
_bm25 = None


# ══════════════════════════════════════════════════════
# Initialisation
# ══════════════════════════════════════════════════════

def _save_corpus() -> None:
    """Persist the BM25 chunk corpus to disk so it survives restarts."""
    try:
        with open(CORPUS_PATH, "w", encoding="utf-8") as f:
            json.dump(_all_chunks, f)
    except Exception as e:
        logger.error("Failed to save BM25 corpus: %s", e)


def _load_corpus() -> None:
    """Load the BM25 corpus from disk on startup."""
    global _all_chunks
    if not os.path.exists(CORPUS_PATH):
        logger.info("[BM25] No corpus file found — BM25 will be empty until documents are ingested.")
        return
    try:
        with open(CORPUS_PATH, "r", encoding="utf-8") as f:
            _all_chunks = json.load(f)
        _rebuild_bm25()
        logger.info("[BM25] Loaded %d chunks from corpus file.", len(_all_chunks))
    except Exception as e:
        logger.error("Failed to load BM25 corpus: %s", e)


def _rebuild_bm25() -> None:
    global _bm25
    if not _all_chunks:
        _bm25 = None
        return
    tokenised = [chunk["text"].lower().split() for chunk in _all_chunks]
    _bm25 = BM25Okapi(tokenised)


def init_pinecone() -> None:
    """
    Connect to Pinecone, initialise LangChain VectorStore wrapper,
    and load the BM25 corpus from disk.
    Called once on FastAPI startup.
    """
    global _index, _vectorstore

    try:
        existing_indexes = [i["name"] for i in _pc.list_indexes()]
        if PINECONE_INDEX_NAME not in existing_indexes:
            _pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            logger.info("[Pinecone] Created index '%s'", PINECONE_INDEX_NAME)
        else:
            logger.info("[Pinecone] Using existing index '%s'", PINECONE_INDEX_NAME)

        _index = _pc.Index(PINECONE_INDEX_NAME)

        from embeddings import get_embedder
        _vectorstore = PineconeVectorStore(
            index=_index,
            embedding=get_embedder(),
            text_key="text",
        )
    except Exception as e:
        logger.error("[Pinecone] Failed to initialize Pinecone: %s", e)
        logger.error("Check your PINECONE_API_KEY and network connection.")

    # Restore BM25 from disk
    _load_corpus()


# ══════════════════════════════════════════════════════
# Write path
# ══════════════════════════════════════════════════════

def upsert_chunks(chunks: list[dict]) -> None:
    """Upload chunks to Pinecone, update in-memory BM25, and persist corpus."""
    if _index is None:
        raise RuntimeError("Call init_pinecone() before upsert_chunks().")

    _index.upsert(vectors=chunks)

    for chunk in chunks:
        _all_chunks.append({
            "id":          chunk["id"],
            "text":        chunk["metadata"]["text"],
            "source":      chunk["metadata"]["source"],
            "chunk_index": chunk["metadata"]["chunk_index"],
        })

    _rebuild_bm25()
    _save_corpus()   # PRODUCTION: persist so restarts don't lose BM25
    logger.info("[Pinecone] Upserted %d chunk(s). Total stored: %d", len(chunks), len(_all_chunks))


# ══════════════════════════════════════════════════════
# Search
# ══════════════════════════════════════════════════════

def semantic_search(query: str) -> list[dict]:
    """Semantic search via LangChain PineconeVectorStore."""
    if _vectorstore is None:
        raise RuntimeError("Call init_pinecone() first.")

    raw = _vectorstore.similarity_search_with_score(query, k=TOP_K * 2)

    results = []
    for doc, score in raw:
        if score >= SIMILARITY_THRESHOLD:
            results.append({
                "id":     str(doc.metadata.get("chunk_index", "")),
                "score":  score,
                "text":   doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
            })
    return results


def bm25_search(query: str) -> list[dict]:
    """Keyword search over all ingested chunks using BM25."""
    if _bm25 is None or not _all_chunks:
        return []

    scores = _bm25.get_scores(query.lower().split())
    ranked = sorted(zip(scores, _all_chunks), key=lambda x: x[0], reverse=True)

    return [
        {"id": c["id"], "score": float(s), "text": c["text"], "source": c["source"]}
        for s, c in ranked[: TOP_K * 2]
        if s > 0
    ]


def _reciprocal_rank_fusion(list_a: list[dict], list_b: list[dict], k: int = 60) -> list[dict]:
    scores: dict[str, float]  = {}
    chunks_by_id: dict[str, dict] = {}

    for rank, item in enumerate(list_a, 1):
        cid = str(item["id"])
        scores[cid]       = scores.get(cid, 0.0) + 1.0 / (k + rank)
        chunks_by_id[cid] = item

    for rank, item in enumerate(list_b, 1):
        cid = str(item["id"])
        scores[cid]       = scores.get(cid, 0.0) + 1.0 / (k + rank)
        chunks_by_id[cid] = item

    return [chunks_by_id[cid] for cid in sorted(scores, key=scores.get, reverse=True)[:TOP_K]]


def hybrid_search(query: str) -> list[dict]:
    """Combine semantic + BM25 via Reciprocal Rank Fusion."""
    sem = semantic_search(query)
    kw  = bm25_search(query)

    if not sem and not kw:
        return []
    if not sem:
        return kw[:TOP_K]
    if not kw:
        return sem[:TOP_K]
    return _reciprocal_rank_fusion(sem, kw)
