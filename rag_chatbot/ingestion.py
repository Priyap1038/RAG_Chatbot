# ingestion.py
# ─────────────────────────────────────────────────────
# Turns a raw text document into vectors stored in Pinecone.
#
# Pipeline:
#   Raw text
#     → RecursiveCharacterTextSplitter  (LangChain)
#     → embed each chunk with OpenAIEmbeddings (LangChain)
#     → upsert to Pinecone with metadata
# ─────────────────────────────────────────────────────

import hashlib

# LANGCHAIN INTEGRATION: replaced custom word-window chunk_text() function
# with RecursiveCharacterTextSplitter which is the LangChain standard splitter.
# It tries to split on paragraphs → sentences → words → chars (in that order)
# to keep semantically coherent chunks.
from langchain_text_splitters import RecursiveCharacterTextSplitter

from embeddings import get_embedding
from vectorstore import upsert_chunks
from config import CHUNK_SIZE, CHUNK_OVERLAP


# LANGCHAIN INTEGRATION: splitter instance (created once, reused for every document)
# Previously: custom chunk_text() that split on whitespace word-by-word
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,      # max characters per chunk (2000 ≈ 400 words)
    chunk_overlap=CHUNK_OVERLAP, # overlap between chunks to preserve context
    length_function=len,
    add_start_index=True,       # stores char offset in metadata (useful for debugging)
)


def ingest_document(text: str, filename: str) -> int:
    """
    Full pipeline: chunk → embed → upsert to Pinecone.

    Args:
        text:     The full text content of the document.
        filename: The original file name (e.g. "hr_policy.md").
                  Stored as metadata so sources can be traced.

    Returns:
        The number of chunks that were ingested.
    """
    print(f"[Ingest] Processing '{filename}' …")

    # LANGCHAIN INTEGRATION: split_text() replaces custom chunk_text()
    chunks = _splitter.split_text(text)
    print(f"[Ingest] Split into {len(chunks)} chunk(s) "
          f"(chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    vectors = []
    for i, chunk in enumerate(chunks):

        # Embed the chunk using LangChain OpenAIEmbeddings (via get_embedding wrapper)
        vector = get_embedding(chunk)

        # Stable unique ID: hash(filename + index) → re-ingesting replaces, not duplicates
        chunk_id = hashlib.md5(f"{filename}_{i}".encode()).hexdigest()

        vectors.append({
            "id": chunk_id,
            "values": vector,
            "metadata": {
                "source": filename,
                "chunk_index": i,
                "text": chunk,      # stored so BM25 can search it
            },
        })

    # Upload all chunks in one batch
    upsert_chunks(vectors)
    print(f"[Ingest] Done — {len(vectors)} chunk(s) uploaded for '{filename}'")

    return len(vectors)
