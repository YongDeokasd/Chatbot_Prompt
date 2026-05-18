"""yfinance candle fetch (§3.4 availability limits). Timestamps UTC (§7)."""
import asyncio
from datetime import datetime, timezone

from app.core.time import index_to_utc, iso_z

_TF_MAP = {
    "1m": "1m", "5m": "5m", "15m": "15m",
    "1h": "1h", "1d": "1d", "1w": "1wk",
}

# max days back from now per timeframe (None = unlimited)
_TF_MAX_DAYS = {
    "1m": 7,
    "5m": 60,
    "15m": 60,
    "1h": 730,
    "4h": 730,  # via 1h resample
    "1d": None,
    "1w": None,
}


def _check_limits(timeframe: str, start: datetime, end: datetime) -> None:
    if timeframe not in _TF_MAX_DAYS:
        raise ValueError(f"Unsupported timeframe: {timeframe}")
    max_days = _TF_MAX_DAYS[timeframe]
    if max_days is None:
        return
    now = datetime.now(timezone.utc)
    age_days = (now - start).total_seconds() / 86400
    if age_days > max_days:
        raise ValueError(
            f"yfinance {timeframe} supports max {max_days} days of history; "
            f"requested range starts {age_days:.0f} days ago"
        )


async def fetch_candles(
    symbol: str, timeframe: str, start: datetime, end: datetime
) -> list[dict]:
    if timeframe == "4h":
        raise ValueError("4h not native to yfinance; resample from 1h")
    _check_limits(timeframe, start, end)
    interval = _TF_MAP.get(timeframe)
    if interval is None:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    def _download():
        import yfinance as yf

        df = yf.download(
            symbol,
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d"),
            interval=interval,
            progress=False,
            auto_adjust=False,
        )
        return df

    df = await asyncio.to_thread(_download)
    if df is None or df.empty:
        return []

    # flatten potential multiindex columns (yfinance >=0.2.40)
    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)

    df.index = index_to_utc(df.index)
    out: list[dict] = []
    for ts, row in df.iterrows():
        out.append(
            {
                "open_time": iso_z(ts.to_pydatetime()),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": float(row["Volume"]),
            }
        )
    return out
