"""Builtin indicators smoke tests — output shape and output_schema (M2)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import numpy as np
import pandas as pd
import pytest
from app.services.indicators.builtin import compute_builtin, BUILTIN_INDICATORS

N = 100

def make_df() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    prices = 100 + rng.normal(0, 1, N).cumsum()
    return pd.DataFrame({
        "open": prices, "high": prices + 0.5,
        "low": prices - 0.5, "close": prices,
        "volume": rng.integers(1000, 5000, N).astype(float),
    })


@pytest.mark.parametrize("name,expected_keys", [
    ("SMA", ["sma"]),
    ("EMA", ["ema"]),
    ("RSI", ["rsi"]),
    ("MACD", ["macd", "signal", "hist"]),
    ("BB", ["upper", "middle", "lower"]),
    ("ATR", ["atr"]),
    ("Volume", ["volume"]),
])
def test_builtin_output_keys(name: str, expected_keys: list[str]):
    df = make_df()
    result = compute_builtin(name, df, {})
    assert set(result.keys()) == set(expected_keys)
    for k in expected_keys:
        assert len(result[k]) == N, f"{name}.{k} wrong length"


def test_builtin_registry_complete():
    names = {b["name"] for b in BUILTIN_INDICATORS}
    assert names == {"SMA", "EMA", "RSI", "MACD", "BB", "ATR", "Volume"}
