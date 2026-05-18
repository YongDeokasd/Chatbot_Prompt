"""Resample 1h→4h correctness tests (M2 §3.4)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.market.resample import resample_1h_to_4h


def _candle(hour: int, o: float, h: float, lo: float, c: float, v: float) -> dict:
    return {
        "open_time": f"2024-01-01T{hour:02d}:00:00Z",
        "open": o, "high": h, "low": lo, "close": c, "volume": v,
    }


def test_4h_aggregation():
    candles = [
        _candle(0,  100, 110,  95, 105, 1000),
        _candle(1,  105, 115,  100, 108, 800),
        _candle(2,  108, 112,  106, 107, 600),
        _candle(3,  107, 120,  105, 115, 900),
        _candle(4,  115, 118,  112, 116, 700),
        _candle(5,  116, 122,  114, 120, 500),
        _candle(6,  120, 125,  118, 122, 400),
        _candle(7,  122, 130,  119, 128, 300),
    ]
    result = resample_1h_to_4h(candles)
    assert len(result) == 2

    bar0 = result[0]
    assert bar0["open_time"] == "2024-01-01T00:00:00Z"
    assert bar0["open"] == 100     # first open
    assert bar0["high"] == 120     # max high
    assert bar0["low"] == 95       # min low
    assert bar0["close"] == 115    # last close
    assert bar0["volume"] == 3300  # sum

    bar1 = result[1]
    assert bar1["open_time"] == "2024-01-01T04:00:00Z"
    assert bar1["open"] == 115
    assert bar1["high"] == 130
    assert bar1["low"] == 112
    assert bar1["close"] == 128
    assert bar1["volume"] == 1900


def test_incomplete_last_bar_included():
    """Partial 4h bar (< 4 hours) should still be returned."""
    candles = [_candle(i, 100 + i, 101 + i, 99 + i, 100 + i, 100) for i in range(6)]
    result = resample_1h_to_4h(candles)
    assert len(result) == 2  # 4 complete + 2 partial
