"""Resample 1h candle dicts to 4h (OHLCV aggregation)."""
import pandas as pd

from app.core.time import iso_z, parse_iso


def resample_1h_to_4h(candles: list[dict]) -> list[dict]:
    if not candles:
        return []
    df = pd.DataFrame(candles)
    df["ts"] = df["open_time"].map(parse_iso)
    df = df.set_index("ts").sort_index()
    agg = df.resample("4h", label="left", closed="left").agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }
    ).dropna(subset=["open"])
    out: list[dict] = []
    for ts, row in agg.iterrows():
        out.append(
            {
                "open_time": iso_z(ts.to_pydatetime()),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
            }
        )
    return out
