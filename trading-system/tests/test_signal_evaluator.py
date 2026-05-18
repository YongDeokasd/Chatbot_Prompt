"""Regression tests for signal evaluator — look-ahead bias (M6/M8 §6.2, §13.1)."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pandas as pd
import pytest
from app.services.backtest.signal_evaluator import EvalContext, eval_condition, eval_logic


def make_ctx(n: int = 20) -> EvalContext:
    idx = pd.RangeIndex(n)
    candles = pd.DataFrame({
        "open":   pd.Series(range(100, 100 + n), dtype=float),
        "high":   pd.Series(range(101, 101 + n), dtype=float),
        "low":    pd.Series(range(99, 99 + n), dtype=float),
        "close":  pd.Series(range(100, 100 + n), dtype=float),
        "volume": pd.Series([1000.0] * n),
    }, index=idx)
    return EvalContext(candles=candles, indicators={})


def test_price_gt_constant():
    """close > 109 should be True only for bars 10+."""
    ctx = make_ctx(20)
    cond = {
        "left": {"type": "price", "source": "close"},
        "operator": ">",
        "right": {"type": "constant", "value": 109.0},
    }
    result = eval_condition(cond, ctx)
    assert result.iloc[9] == False   # close=109, not > 109
    assert result.iloc[10] == True   # close=110


def test_shift_no_lookahead():
    """shift=1 should reference the previous bar — never a future bar."""
    ctx = make_ctx(10)
    cond = {
        "left": {"type": "price", "source": "close", "shift": 1},
        "operator": ">",
        "right": {"type": "constant", "value": 104.0},
    }
    result = eval_condition(cond, ctx)
    # Bar 0: shift(1) → NaN → False
    assert pd.isna(result.iloc[0]) or result.iloc[0] == False
    # Bar 6: close.shift(1) = close[5] = 105 > 104 → True
    assert result.iloc[6] == True


def test_cross_above_no_lookahead():
    """cross_above must use current and previous bar only."""
    ctx = make_ctx(20)
    # Indicator: flat at 105 for first 10 bars, then 115
    vals = [105.0] * 10 + [115.0] * 10
    ctx.indicators["ind1"] = {"val": pd.Series(vals, index=ctx.candles.index)}

    cond = {
        "left": {"type": "indicator", "indicator_id": "ind1", "output_key": "val"},
        "operator": "cross_above",
        "right": {"type": "constant", "value": 110.0},
    }
    result = eval_condition(cond, ctx)
    # Cross happens at bar 10 (prev=105 ≤ 110, cur=115 > 110)
    assert result.iloc[10] == True
    # No other bar should be True
    other = result.drop(10)
    assert not other.any()


def test_and_logic():
    ctx = make_ctx(10)
    c1 = {"left": {"type": "price", "source": "close"}, "operator": ">", "right": {"type": "constant", "value": 104.0}}
    c2 = {"left": {"type": "price", "source": "close"}, "operator": "<", "right": {"type": "constant", "value": 108.0}}
    result = eval_logic([c1, c2], "AND", ctx)
    # close 105,106,107 satisfy both
    assert result.iloc[5] == True
    assert result.iloc[7] == True
    assert result.iloc[8] == False  # close=108, not < 108


def test_or_logic():
    ctx = make_ctx(10)
    c1 = {"left": {"type": "price", "source": "close"}, "operator": "<", "right": {"type": "constant", "value": 102.0}}
    c2 = {"left": {"type": "price", "source": "close"}, "operator": ">", "right": {"type": "constant", "value": 107.0}}
    result = eval_logic([c1, c2], "OR", ctx)
    assert result.iloc[0] == True   # close=100 < 102
    assert result.iloc[8] == True   # close=108 > 107
    assert result.iloc[4] == False  # close=104, neither
