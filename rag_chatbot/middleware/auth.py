# middleware/auth.py
# ─────────────────────────────────────────────────────
# Optional Bearer-token API key authentication.
# Enabled only when API_KEY is set in .env.
# If API_KEY is blank, all requests pass through untouched.
# ─────────────────────────────────────────────────────

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import API_KEY

logger = logging.getLogger(__name__)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Validates Bearer token on all /api/* routes.
    Skipped automatically if API_KEY is not configured.
    """

    async def dispatch(self, request: Request, call_next):
        # Auth disabled — pass through
        if not API_KEY:
            return await call_next(request)

        # Only protect /api/* endpoints
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        # Health check is always public
        if request.url.path == "/api/health":
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            logger.warning("Unauthorized request to %s", request.url.path)
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization header. "
                                   "Use: Authorization: Bearer <API_KEY>"},
            )

        token = auth_header[len("Bearer "):]
        if token != API_KEY:
            logger.warning("Invalid API key for %s", request.url.path)
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid API key."},
            )

        return await call_next(request)
