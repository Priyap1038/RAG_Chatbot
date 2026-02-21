# ingest_docs.py
# ─────────────────────────────────────────────────────
# One-shot script: load docs from the docs/ folder into Pinecone.
#
# LANGCHAIN INTEGRATION:
#   - TextLoader (langchain_community) replaces open() + f.read()
#   - Supports .txt and .md files
#
# Usage:
#   python ingest_docs.py
# ─────────────────────────────────────────────────────

import os

# LANGCHAIN INTEGRATION: TextLoader replaces manual open() + f.read()
# It returns a list of LangChain Document objects with
#   .page_content  → the text
#   .metadata      → {"source": filepath}
from langchain_community.document_loaders import TextLoader

from vectorstore import init_pinecone
from ingestion   import ingest_document

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")


def main():
    print("=" * 50)
    print("  Acme Tech Solutions — Document Ingestion")
    print("=" * 50)

    init_pinecone()

    # Find all .md and .txt files
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

        # LANGCHAIN INTEGRATION: TextLoader replaces open(filepath).read()
        # autodetect_encoding=True handles different file encodings gracefully
        loader = TextLoader(filepath, autodetect_encoding=True)
        docs   = loader.load()          # returns List[Document]

        # Each file loads as a single Document; use its page_content
        text = docs[0].page_content

        print(f"\n→ Ingesting '{filename}' ({len(text.split())} words) …")
        count = ingest_document(text, filename)
        total_chunks += count
        print(f"  ✓  {count} chunk(s) stored")

    print("\n" + "=" * 50)
    print(f"  Done! {total_chunks} total chunk(s) in Pinecone.")
    print("  Start the server:")
    print("  uvicorn main:app --reload --port 8000")
    print("=" * 50)


if __name__ == "__main__":
    main()
