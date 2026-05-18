"""7 builtin indicators via pandas-ta."""
import pandas as pd
import pandas_ta as ta


def _series(s: pd.Series) -> list:
    return [None if pd.isna(v) else float(v) for v in s]


def compute_builtin(
    name: str, candles_df: pd.DataFrame, params: dict
) -> dict[str, list]:
    df = candles_df
    name = name.upper()

    if name == "SMA":
        length = int(params.get("length", 20))
        return {"sma": _series(ta.sma(df["close"], length=length))}

    if name == "EMA":
        length = int(params.get("length", 20))
        return {"ema": _series(ta.ema(df["close"], length=length))}

    if name == "RSI":
        length = int(params.get("length", 14))
        return {"rsi": _series(ta.rsi(df["close"], length=length))}

    if name == "MACD":
        fast = int(params.get("fast", 12))
        slow = int(params.get("slow", 26))
        signal = int(params.get("signal", 9))
        m = ta.macd(df["close"], fast=fast, slow=slow, signal=signal)
        cols = list(m.columns)
        return {
            "macd": _series(m[cols[0]]),
            "hist": _series(m[cols[1]]),
            "signal": _series(m[cols[2]]),
        }

    if name == "BB":
        length = int(params.get("length", 20))
        std = float(params.get("std", 2.0))
        b = ta.bbands(df["close"], length=length, std=std)
        cols = list(b.columns)
        return {
            "lower": _series(b[cols[0]]),
            "middle": _series(b[cols[1]]),
            "upper": _series(b[cols[2]]),
        }

    if name == "ATR":
        length = int(params.get("length", 14))
        return {
            "atr": _series(
                ta.atr(df["high"], df["low"], df["close"], length=length)
            )
        }

    if name == "VOLUME":
        return {"volume": _series(df["volume"])}

    raise ValueError(f"Unknown builtin indicator: {name}")


BUILTIN_INDICATORS = [
    {
        "id": "sma",
        "name": "SMA",
        "output_schema": {"outputs": ["sma"]},
        "params_schema": [
            {"name": "length", "type": "int", "default": 20, "min": 1, "max": 1000}
        ],
    },
    {
        "id": "ema",
        "name": "EMA",
        "output_schema": {"outputs": ["ema"]},
        "params_schema": [
            {"name": "length", "type": "int", "default": 20, "min": 1, "max": 1000}
        ],
    },
    {
        "id": "rsi",
        "name": "RSI",
        "output_schema": {"outputs": ["rsi"]},
        "params_schema": [
            {"name": "length", "type": "int", "default": 14, "min": 1, "max": 1000}
        ],
    },
    {
        "id": "macd",
        "name": "MACD",
        "output_schema": {"outputs": ["macd", "signal", "hist"]},
        "params_schema": [
            {"name": "fast", "type": "int", "default": 12, "min": 1, "max": 1000},
            {"name": "slow", "type": "int", "default": 26, "min": 1, "max": 1000},
            {"name": "signal", "type": "int", "default": 9, "min": 1, "max": 1000},
        ],
    },
    {
        "id": "bb",
        "name": "BB",
        "output_schema": {"outputs": ["upper", "middle", "lower"]},
        "params_schema": [
            {"name": "length", "type": "int", "default": 20, "min": 1, "max": 1000},
            {"name": "std", "type": "float", "default": 2.0, "min": 0.1, "max": 10},
        ],
    },
    {
        "id": "atr",
        "name": "ATR",
        "output_schema": {"outputs": ["atr"]},
        "params_schema": [
            {"name": "length", "type": "int", "default": 14, "min": 1, "max": 1000}
        ],
    },
    {
        "id": "volume",
        "name": "Volume",
        "output_schema": {"outputs": ["volume"]},
        "params_schema": [],
    },
]

BUILTIN_NAMES = {b["name"].upper() for b in BUILTIN_INDICATORS}
