"""Market data orchestration: cache, fetch, resample (§3.4)."""
from datetime import datetime

from sqlalchemy import select

from app.core.time import iso_z, parse_iso, to_utc
from app.db import SessionLocal
from app.models import CandleCache
from app.services.market import binance, yfinance_service
from app.services.market.resample import resample_1h_to_4h

ALL_TF = ["1m", "5m", "15m", "1h", "4h", "1d", "1w"]

# source+timeframe -> max history days (None = unlimited)
TIMEFRAME_LIMITS: dict[str, dict[str, int | None]] = {
    "binance": {tf: None for tf in ALL_TF},
    "yfinance": {
        "1m": 7,
        "5m": 60,
        "15m": 60,
        "1h": 730,
        "4h": 730,
        "1d": None,
        "1w": None,
    },
}

EXCHANGE_TIMEFRAMES: dict[str, list[str]] = {
    "binance": list(ALL_TF),
    "yfinance": list(ALL_TF),
}


def get_available_timeframes(exchange: str) -> list[dict]:
    if exchange not in EXCHANGE_TIMEFRAMES:
        raise ValueError(f"Unknown exchange: {exchange}")
    limits = TIMEFRAME_LIMITS[exchange]
    return [
        {"timeframe": tf, "available": True, "max_days": limits.get(tf)}
        for tf in EXCHANGE_TIMEFRAMES[exchange]
    ]


async def _read_cache(
    symbol: str, exchange: str, timeframe: str, start: datetime, end: datetime
) -> list[dict]:
    async with SessionLocal() as s:
        rows = (
            await s.execute(
                select(CandleCache)
                .where(
                    CandleCache.symbol == symbol,
                    CandleCache.exchange == exchange,
                    CandleCache.timeframe == timeframe,
                    CandleCache.open_time >= start,
                    CandleCache.open_time <= end,
                )
                .order_by(CandleCache.open_time)
            )
        ).scalars().all()
    return [
        {
            "open_time": iso_z(r.open_time),
            "open": float(r.open),
            "high": float(r.high),
            "low": float(r.low),
            "close": float(r.close),
            "volume": float(r.volume),
        }
        for r in rows
    ]


async def _write_cache(
    symbol: str, exchange: str, timeframe: str, candles: list[dict]
) -> None:
    if not candles:
        return
    from sqlalchemy.dialects.postgresql import insert

    rows = [
        {
            "symbol": symbol,
            "exchange": exchange,
            "timeframe": timeframe,
            "open_time": parse_iso(c["open_time"]),
            "open": c["open"],
            "high": c["high"],
            "low": c["low"],
            "close": c["close"],
            "volume": c["volume"],
        }
        for c in candles
    ]
    async with SessionLocal() as s:
        stmt = insert(CandleCache).values(rows)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=["symbol", "exchange", "timeframe", "open_time"]
        )
        await s.execute(stmt)
        await s.commit()


def _expected_count(timeframe: str, start: datetime, end: datetime) -> int:
    secs = {
        "1m": 60, "5m": 300, "15m": 900, "1h": 3600,
        "4h": 14400, "1d": 86400, "1w": 604800,
    }[timeframe]
    span = (end - start).total_seconds()
    return max(int(span / secs), 1)


async def get_candles(
    symbol: str, exchange: str, timeframe: str, start: datetime, end: datetime
) -> list[dict]:
    start, end = to_utc(start), to_utc(end)

    cached = await _read_cache(symbol, exchange, timeframe, start, end)
    expected = _expected_count(timeframe, start, end)
    if cached and len(cached) >= expected * 0.9:
        return cached

    if exchange == "binance":
        fetched = await binance.fetch_candles(symbol, timeframe, start, end)
    elif exchange == "yfinance":
        if timeframe == "4h":
            base = await yfinance_service.fetch_candles(symbol, "1h", start, end)
            fetched = resample_1h_to_4h(base)
        else:
            fetched = await yfinance_service.fetch_candles(
                symbol, timeframe, start, end
            )
    else:
        raise ValueError(f"Unknown exchange: {exchange}")

    await _write_cache(symbol, exchange, timeframe, fetched)
    return fetched
