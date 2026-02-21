# routes/ingest.py
# ─────────────────────────────────────────────────────
# POST /api/ingest
#
# Two ways to upload a document:
#   • JSON body  → { "text": "...", "filename": "doc.md" }
#   • File upload → multipart form-data with a file field
# ─────────────────────────────────────────────────────

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from ingestion import ingest_document
import aiofiles

router = APIRouter()


# ── JSON body schema ──────────────────────────────────
class IngestRequest(BaseModel):
    text: str
    filename: str = "document.txt"


# ── Endpoint 1: JSON text input ───────────────────────
@router.post("/api/ingest")
async def ingest_text(req: IngestRequest):
    """
    Ingest a plain text document sent as JSON.

    Example body:
        { "text": "Acme was founded in 2005...", "filename": "history.md" }
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    count = ingest_document(req.text, req.filename)
    return {"message": f"Ingested {count} chunk(s) from '{req.filename}'"}


# ── Endpoint 2: File upload ───────────────────────────
@router.post("/api/ingest/file")
async def ingest_file(file: UploadFile = File(...)):
    """
    Ingest a text file uploaded via multipart form-data.

    Supported formats: .txt, .md  (any plain-text file).
    """
    # Only accept plain text / markdown
    allowed = {".txt", ".md"}
    ext = "." + file.filename.split(".")[-1].lower()
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Only .txt and .md files are supported. Got '{file.filename}'.",
        )

    # Read the uploaded bytes
    raw_bytes = await file.read()

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded text.",
        )

    if not text.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    count = ingest_document(text, file.filename)
    return {"message": f"Ingested {count} chunk(s) from '{file.filename}'"}
