import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import (
    ai,
    backtests,
    benchmarks,
    indicators,
    market,
    strategies,
    symbols,
    ws,
)
from app.services.realtime.streamer import streamer

log = structlog.get_logger()

app = FastAPI(title="Trading System API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router)
app.include_router(symbols.router)
app.include_router(indicators.router)
app.include_router(ai.router)
app.include_router(strategies.router)
app.include_router(backtests.router)
app.include_router(benchmarks.router)
app.include_router(ws.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.on_event("startup")
async def startup() -> None:
    token = settings.ensure_local_token()
    log.info("startup", local_token_set=bool(token))
    try:
        await streamer.start()
    except Exception as e:  # noqa: BLE001
        log.warning("streamer_start_failed", error=str(e))


@app.on_event("shutdown")
async def shutdown() -> None:
    try:
        await streamer.stop()
    except Exception as e:  # noqa: BLE001
        log.warning("streamer_stop_failed", error=str(e))


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
