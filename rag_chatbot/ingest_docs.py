# ingest_docs.py
# ─────────────────────────────────────────────────────
# One-shot script: load docs from the docs/ folder into Pinecone.
# ─────────────────────────────────────────────────────

import os
import hashlib

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from vectorstore import init_pinecone, upsert_chunks
from embeddings import get_embedding
from config import CHUNK_SIZE, CHUNK_OVERLAP

DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    add_start_index=True,
)


def ingest_document(text: str, filename: str) -> int:
    """
    Full pipeline: chunk -> embed -> upsert to Pinecone.
    """
    print(f"[Ingest] Processing '{filename}' ...")

    chunks = _splitter.split_text(text)
    print(f"[Ingest] Split into {len(chunks)} chunk(s) "
          f"(chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    vectors = []
    for i, chunk in enumerate(chunks):
        vector = get_embedding(chunk)
        chunk_id = hashlib.md5(f"{filename}_{i}".encode()).hexdigest()

        vectors.append({
            "id": chunk_id,
            "values": vector,
            "metadata": {
                "source": filename,
                "chunk_index": i,
                "text": chunk,
            },
        })

    upsert_chunks(vectors)
    print(f"[Ingest] Done — {len(vectors)} chunk(s) uploaded for '{filename}'")
    return len(vectors)


def main():
    print("=" * 50)
    print("  Acme Tech Solutions — Document Ingestion")
    print("=" * 50)

    init_pinecone()

    doc_files = [
        f for f in os.listdir(DOCS_DIR)
        if f.endswith((".md", ".txt"))
    ]

    if not doc_files:
        print(f"No documents found in: {DOCS_DIR}")
        return

    total_chunks = 0
    for filename in doc_files:
        filepath = os.path.join(DOCS_DIR, filename)
        
        loader = TextLoader(filepath, autodetect_encoding=True)
        docs   = loader.load()
        text = docs[0].page_content

        print(f"\n-> Ingesting '{filename}' ({len(text.split())} words) ...")
        count = ingest_document(text, filename)
        total_chunks += count
        print(f"  V  {count} chunk(s) stored")

    print("\n" + "=" * 50)
    print(f"  Done! {total_chunks} total chunk(s) in Pinecone.")
    print("  Start the server:")
    print("  uvicorn main:app --reload --port 8000")
    print("=" * 50)


if __name__ == "__main__":
    main()
