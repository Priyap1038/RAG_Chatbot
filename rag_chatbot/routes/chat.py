# routes/chat.py
# ─────────────────────────────────────────────────────
# POST /api/chat
# ─────────────────────────────────────────────────────

import json
import re

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from vectorstore import hybrid_search
from memory import add_message, get_recent
from config import (
    CHAT_TEMPERATURE,
    OPENAI_API_KEY, OPENAI_CHAT_MODEL,
)

router = APIRouter()

from langchain_openai import ChatOpenAI
_llm      = ChatOpenAI(model=OPENAI_CHAT_MODEL, temperature=CHAT_TEMPERATURE,
                       streaming=True, openai_api_key=OPENAI_API_KEY, max_tokens=512)
_llm_warm = ChatOpenAI(model=OPENAI_CHAT_MODEL, temperature=0.7,
                       streaming=True, openai_api_key=OPENAI_API_KEY, max_tokens=256)

_parser = StrOutputParser()

# ── General query detector ────────────────────────────
_GENERAL_PATTERNS = re.compile(
    r"""
    ^\s*(
        hi+|hello+|hey+|howdy|hiya|yo+|sup|
        good\s*(morning|afternoon|evening|night|day)|
        greetings|namaste|
        how\s+are\s+(you|u)|
        how('?s| is)\s+(it\s+going|everything)|
        what('?s|\s+is)\s+up|wassup|
        who\s+are\s+you|what\s+are\s+you|
        (what\s+can\s+you\s+do|what\s+do\s+you\s+do)|
        are\s+you\s+(a\s+)?(bot|ai|robot|assistant)|
        thanks?|thank\s+you|thx|ty|
        bye(-?bye)?|goodbye|see\s+ya|take\s+care|
        (what('?s|\s+is)\s+)?your\s+name|
        (can\s+you\s+)?help\s+(me)?
    )\s*[?!.]*\s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

def is_general_query(text: str) -> bool:
    return bool(_GENERAL_PATTERNS.match(text.strip()))

# ── LANGCHAIN INTEGRATION: prompt templates ───────────

_GENERAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a friendly AI assistant for Acme Tech Solutions. "
     "Have natural, warm conversations. Keep responses short and friendly. "
     "If asked what you can do, mention you can answer questions about "
     "Acme Tech Solutions — its history, products, and HR policies."),
    ("placeholder", "{history}"),
    ("human", "{question}"),
])

_RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful assistant for Acme Tech Solutions. "
     "Answer ONLY using the information in the CONTEXT below. "
     "Do NOT use any outside knowledge. "
     "Do NOT mention file names, document names, or sources. "
     "Just give a clear, direct, concise answer. "
     "If the context lacks enough information, say: "
     "\"I don't have enough information to answer that accurately.\"\n\n"
     "CONTEXT:\n{context}"),
    ("placeholder", "{history}"),
    ("human", "{question}"),
])

_general_chain = _GENERAL_PROMPT | _llm_warm | _parser
_rag_chain     = _RAG_PROMPT     | _llm       | _parser


def _format_history(session_id: str) -> list:
    recent = get_recent(session_id)
    return [
        ("human" if msg["role"] == "user" else "ai", msg["content"])
        for msg in recent
    ]


async def _stream_chain(session_id: str, user_message: str, chain, inputs: dict):
    full_answer = ""
    try:
        async for token in chain.astream(inputs):
            full_answer += token
            yield f"data: {json.dumps({'token': token})}\n\n"
    except Exception as e:
        err = str(e)
        if "api_key" in err.lower() or "auth" in err.lower() or "401" in err:
            full_answer = (
                "⚠️ OpenAI API key missing or invalid. "
                "Add OPENAI_API_KEY to .env and restart the server."
            )
        else:
            full_answer = f"⚠️ Error: {err[:120]}"
        yield f"data: {json.dumps({'token': full_answer})}\n\n"

    add_message(session_id, "user", user_message)
    add_message(session_id, "assistant", full_answer)
    yield f"data: {json.dumps({'sources': [], 'done': True})}\n\n"


class ChatRequest(BaseModel):
    message: str
    session_id: str


@router.post("/api/chat")
async def chat(req: ChatRequest):
    history = _format_history(req.session_id)

    # PATH 1: Greeting
    if is_general_query(req.message):
        return StreamingResponse(
            _stream_chain(req.session_id, req.message, _general_chain,
                          {"question": req.message, "history": history}),
            media_type="text/event-stream",
        )

    # PATH 2 & 3: Domain question
    chunks = hybrid_search(req.message)

    if not chunks:
        async def out_of_scope():
            answer = (
                "I can only answer questions related to Acme Tech Solutions — "
                "such as company history, products, or HR policies. "
                "I don't have information about that topic."
            )
            add_message(req.session_id, "user", req.message)
            add_message(req.session_id, "assistant", answer)
            yield f"data: {json.dumps({'token': answer})}\n\n"
            yield f"data: {json.dumps({'sources': [], 'done': True})}\n\n"
        return StreamingResponse(out_of_scope(), media_type="text/event-stream")

    context = "\n\n".join(c["text"] for c in chunks)
    return StreamingResponse(
        _stream_chain(req.session_id, req.message, _rag_chain,
                      {"question": req.message, "context": context, "history": history}),
        media_type="text/event-stream",
    )
