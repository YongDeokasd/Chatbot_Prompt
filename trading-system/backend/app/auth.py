"""Local token auth (§8.1).

All /api/* requests require `Authorization: Bearer <token>`.
WS uses `?token=...`. Origin restricted to localhost / 127.0.0.1.
"""
from fastapi import HTTPException, Request, status

from app.config import settings

_ALLOWED_HOSTS = ("localhost", "127.0.0.1")


def _origin_ok(request: Request) -> bool:
    origin = request.headers.get("origin")
    if origin is None:
        return True  # non-browser client (curl, tests)
    return any(h in origin for h in _ALLOWED_HOSTS)


async def require_token(request: Request) -> None:
    if not _origin_ok(request):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Origin not allowed")
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    if auth.removeprefix("Bearer ").strip() != settings.local_api_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")


def check_ws_token(token: str | None) -> bool:
    return token == settings.local_api_token
