"""AI Pine -> Python conversion via Anthropic (§10)."""
import datetime as _dt
import hashlib
import json
import re

import redis.asyncio as aioredis

from app.config import settings
from app.core.prompts import (
    PINE_FEW_SHOTS,
    PINE_SYSTEM_PROMPT,
    WHITELIST_UNSUPPORTED,
)

_CACHE_TTL = 24 * 3600
_redis: aioredis.Redis | None = None


def _r() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.Redis(
            host=settings.redis_host, port=settings.redis_port,
            decode_responses=True,
        )
    return _redis


def _scan_unsupported(pine_code: str) -> list[str]:
    found = []
    for tok in WHITELIST_UNSUPPORTED:
        pat = r"\b" + re.escape(tok) + r"\b"
        if re.search(pat, pine_code):
            found.append(tok)
    return sorted(set(found))


async def _check_daily_limit() -> None:
    key = "ai:calls:" + _dt.date.today().isoformat()
    r = _r()
    n = await r.incr(key)
    if n == 1:
        await r.expire(key, 86400)
    if n > settings.anthropic_daily_call_limit:
        raise ValueError(
            f"Daily AI call limit reached ({settings.anthropic_daily_call_limit})"
        )


async def convert_pine_to_python(pine_code: str) -> dict:
    unsupported = _scan_unsupported(pine_code)
    if unsupported:
        raise ValueError(json.dumps({"unsupported_tokens": unsupported}))

    cache_key = "ai:pine:" + hashlib.sha256(pine_code.encode()).hexdigest()
    r = _r()
    try:
        cached = await r.get(cache_key)
    except Exception:
        cached = None
    if cached:
        return json.loads(cached)

    await _check_daily_limit()

    import anthropic

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    messages = []
    for pine, py in PINE_FEW_SHOTS:
        messages.append({"role": "user", "content": pine})
        messages.append({
            "role": "assistant",
            "content": json.dumps({
                "python_code": py,
                "params_schema": [],
                "output_schema": {"outputs": []},
                "explanation": "",
                "warnings": [],
                "unsupported_tokens": [],
            }),
        })
    messages.append({"role": "user", "content": pine_code})

    resp = await client.messages.create(
        model=settings.anthropic_model,
        max_tokens=4096,
        system=PINE_SYSTEM_PROMPT,
        messages=messages,
    )
    text = "".join(
        b.text for b in resp.content if getattr(b, "type", None) == "text"
    ).strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            raise ValueError("AI returned non-JSON response")
        data = json.loads(m.group(0))

    model_unsupported = data.get("unsupported_tokens") or []
    if model_unsupported:
        raise ValueError(json.dumps({"unsupported_tokens": model_unsupported}))

    out = {
        "python_code": data.get("python_code", ""),
        "params_schema": data.get("params_schema", []),
        "output_schema": data.get("output_schema", {"outputs": []}),
        "explanation": data.get("explanation", ""),
        "warnings": data.get("warnings", []),
    }
    try:
        await r.set(cache_key, json.dumps(out), ex=_CACHE_TTL)
    except Exception:
        pass
    return out
