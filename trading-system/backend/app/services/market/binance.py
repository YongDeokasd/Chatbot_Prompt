"""Binance public REST candle fetch (§3.4: Crypto unlimited history).

Timestamps are open_time, UTC (§7). Respects Binance rate limits with
a small retry/backoff on transient errors.
"""
import asyncio
from datetime import datetime

import httpx

from app.core.time import iso_z

_BASE = "https://api.binance.com/api/v3/klines"
_TF_MAP = {
    "1m": "1m", "5m": "5m", "15m": "15m",
    "1h": "1h", "4h": "4h", "1d": "1d", "1w": "1w",
}


async def fetch_candles(
    symbol: str, timeframe: str, start: datetime, end: datetime, limit: int = 1000
) -> list[dict]:
    interval = _TF_MAP.get(timeframe)
    if interval is None:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "startTime": int(start.timestamp() * 1000),
        "endTime": int(end.timestamp() * 1000),
        "limit": limit,
    }

    last_exc: Exception | None = None
    for attempt in range(4):
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(_BASE, params=params)
                resp.raise_for_status()
                rows = resp.json()
                break
        except (httpx.HTTPError, httpx.TransportError) as exc:
            last_exc = exc
            await asyncio.sleep(2 ** attempt)
    else:
        raise RuntimeError(f"Binance fetch failed: {last_exc}")

    out: list[dict] = []
    for r in rows:
        open_dt = datetime.utcfromtimestamp(r[0] / 1000)
        out.append(
            {
                "open_time": iso_z(open_dt),
                "open": float(r[1]),
                "high": float(r[2]),
                "low": float(r[3]),
                "close": float(r[4]),
                "volume": float(r[5]),
            }
        )
    return out
