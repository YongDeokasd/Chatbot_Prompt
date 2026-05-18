"""UTC / ISO 8601 helpers — global timestamp convention (§7).

All backend processing, DB storage and API I/O are UTC.
Format: ISO 8601 with mandatory 'Z' suffix. Candles use open time.
"""
from datetime import datetime, timezone

import pandas as pd


def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def iso_z(dt: datetime) -> str:
    """Serialize as '2025-01-01T00:00:00Z'."""
    return to_utc(dt).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(value: str) -> datetime:
    return to_utc(datetime.fromisoformat(value.replace("Z", "+00:00")))


def index_to_utc(idx: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """yfinance returns exchange-local tz -> convert to UTC (§7)."""
    if idx.tz is None:
        return idx.tz_localize("UTC")
    return idx.tz_convert("UTC")
