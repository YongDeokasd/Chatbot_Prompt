"""WebSocket price fan-out from Redis pub/sub (§11)."""
import redis.asyncio as aioredis
import structlog
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.auth import check_ws_token
from app.config import settings

log = structlog.get_logger()
router = APIRouter(prefix="/api/ws", tags=["ws"])

_CHANNEL = "prices"


@router.websocket("/prices")
async def ws_prices(websocket: WebSocket, token: str | None = Query(default=None)):
    if not check_ws_token(token):
        await websocket.close(code=4401)
        return
    await websocket.accept()

    r = aioredis.Redis(
        host=settings.redis_host, port=settings.redis_port,
        decode_responses=True,
    )
    pubsub = r.pubsub()
    await pubsub.subscribe(_CHANNEL)
    try:
        async for message in pubsub.listen():
            if message.get("type") != "message":
                continue
            await websocket.send_text(message["data"])
    except WebSocketDisconnect:
        pass
    except Exception as e:  # noqa: BLE001
        log.warning("ws_error", error=str(e))
    finally:
        await pubsub.unsubscribe(_CHANNEL)
        await pubsub.aclose()
        await r.aclose()
