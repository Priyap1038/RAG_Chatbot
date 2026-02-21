# routes/history.py
# ─────────────────────────────────────────────────────
# GET /api/history/{session_id}
# Returns the full chat history for one session.
# ─────────────────────────────────────────────────────

from fastapi import APIRouter
from memory import get_history

router = APIRouter()


@router.get("/api/history/{session_id}")
async def get_session_history(session_id: str):
    """
    Fetch all messages for a chat session.

    Args:
        session_id: The unique session identifier.

    Returns:
        { "session_id": "...", "messages": [...] }
    """
    messages = get_history(session_id)
    return {
        "session_id": session_id,
        "messages": messages,
    }
