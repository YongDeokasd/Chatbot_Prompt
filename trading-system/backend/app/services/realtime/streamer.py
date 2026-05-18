"""Realtime price streamer: Binance WS + yfinance polling -> Redis (§11)."""
import asyncio
import json

import redis.asyncio as aioredis
import structlog

from app.config import settings
from app.core.time import iso_z
from app.db import SessionLocal

log = structlog.get_logger()

_CHANNEL = "prices"
_BINANCE_WS = "wss://stream.binance.com:9443/ws/{stream}@miniTicker"


class RealtimeStreamer:
    def __init__(self) -> None:
        self._tasks: list[asyncio.Task] = []
        self._running = False
        self._redis: aioredis.Redis | None = None

    def _r(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.Redis(
                host=settings.redis_host, port=settings.redis_port,
                decode_responses=True,
            )
        return self._redis

    async def _load_symbols(self) -> tuple[list[str], list[str]]:
        from sqlalchemy import select

        from app.models import BenchmarkSymbol

        async with SessionLocal() as s:
            rows = (await s.execute(
                select(BenchmarkSymbol).where(BenchmarkSymbol.active.is_(True))
            )).scalars().all()
        crypto = [r.symbol for r in rows if r.exchange == "binance"]
        stocks = [r.symbol for r in rows if r.exchange == "yfinance"]
        return crypto, stocks

    async def _publish(self, symbol: str, exchange: str, price: float) -> None:
        from datetime import datetime, timezone

        msg = json.dumps({
            "symbol": symbol,
            "exchange": exchange,
            "price": price,
            "time": iso_z(datetime.now(timezone.utc)),
        })
        try:
            await self._r().publish(_CHANNEL, msg)
        except Exception as e:  # noqa: BLE001
            log.warning("publish_failed", error=str(e))

    async def _binance_loop(self, symbols: list[str]) -> None:
        import websockets

        stream = "/".join(f"{s.lower()}@miniTicker" for s in symbols)
        url = f"wss://stream.binance.com:9443/stream?streams={stream}"
        while self._running:
            try:
                async with websockets.connect(url, ping_interval=20) as ws:
                    while self._running:
                        raw = await ws.recv()
                        payload = json.loads(raw)
                        data = payload.get("data", payload)
                        sym = data.get("s")
                        price = data.get("c")
                        if sym and price is not None:
                            await self._publish(sym, "binance", float(price))
            except asyncio.CancelledError:
                raise
            except Exception as e:  # noqa: BLE001
                log.warning("binance_ws_error", error=str(e))
                await asyncio.sleep(5)

    async def _yfinance_loop(self, symbols: list[str]) -> None:
        while self._running:
            try:
                def _poll() -> dict[str, float]:
                    import yfinance as yf

                    out: dict[str, float] = {}
                    for sym in symbols:
                        try:
                            t = yf.Ticker(sym)
                            data = t.fast_info
                            p = getattr(data, "last_price", None)
                            if p is not None:
                                out[sym] = float(p)
                        except Exception:  # noqa: BLE001
                            continue
                    return out

                prices = await asyncio.to_thread(_poll)
                for sym, p in prices.items():
                    await self._publish(sym, "yfinance", p)
            except asyncio.CancelledError:
                raise
            except Exception as e:  # noqa: BLE001
                log.warning("yfinance_poll_error", error=str(e))
            await asyncio.sleep(30)

    async def start(self) -> None:
        if self._running:
            return
        crypto, stocks = await self._load_symbols()
        if not crypto and not stocks:
            log.info("streamer_no_symbols")
            return
        self._running = True
        if crypto:
            self._tasks.append(
                asyncio.create_task(self._binance_loop(crypto))
            )
        if stocks:
            self._tasks.append(
                asyncio.create_task(self._yfinance_loop(stocks))
            )
        log.info("streamer_started", crypto=len(crypto), stocks=len(stocks))

    async def stop(self) -> None:
        self._running = False
        for t in self._tasks:
            t.cancel()
        for t in self._tasks:
            try:
                await t
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
        self._tasks.clear()
        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None
        log.info("streamer_stopped")


streamer = RealtimeStreamer()
