# routes/session.py
# ─────────────────────────────────────────────────────
# POST /api/session          → register a new empty session
# DELETE /api/session/{id}   → remove a session
# ─────────────────────────────────────────────────────

from fastapi import APIRouter
from pydantic import BaseModel
from memory import register_session, delete_session

router = APIRouter()


class SessionCreate(BaseModel):
    session_id: str


@router.post("/api/session")
async def create_session(req: SessionCreate):
    """
    Register a new session immediately when the user clicks 'New Chat'.
    This makes the session visible in GET / right away, even before
    any message has been sent.
    """
    register_session(req.session_id)
    return {"message": f"Session '{req.session_id}' created.", "session_id": req.session_id}


@router.delete("/api/session/{session_id}")
async def remove_session(session_id: str):
    """Delete a chat session and all its messages."""
    delete_session(session_id)
    return {"message": f"Session '{session_id}' deleted successfully."}
