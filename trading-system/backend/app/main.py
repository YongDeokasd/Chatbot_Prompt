import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import market

log = structlog.get_logger()

app = FastAPI(title="Trading System API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router)


@app.on_event("startup")
async def startup() -> None:
    token = settings.ensure_local_token()
    log.info("startup", local_token_set=bool(token))


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
