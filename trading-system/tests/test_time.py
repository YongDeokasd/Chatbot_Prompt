"""UTC / timezone convention tests (M8 §7, §13.1)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from datetime import datetime, timezone
import pandas as pd
from app.core.time import iso_z, parse_iso, to_utc, index_to_utc


def test_iso_z_produces_z_suffix():
    dt = datetime(2024, 1, 15, 8, 0, 0, tzinfo=timezone.utc)
    assert iso_z(dt).endswith("Z")
    assert "T" in iso_z(dt)


def test_parse_iso_roundtrip():
    s = "2024-06-01T12:00:00Z"
    dt = parse_iso(s)
    assert dt.tzinfo is not None
    assert dt.tzinfo == timezone.utc
    assert iso_z(dt) == s


def test_naive_becomes_utc():
    naive = datetime(2024, 1, 1, 0, 0, 0)
    utc = to_utc(naive)
    assert utc.tzinfo == timezone.utc


def test_index_to_utc_localizes_naive():
    idx = pd.date_range("2024-01-01", periods=5, freq="1h")
    result = index_to_utc(idx)
    assert result.tz is not None
    assert str(result.tz) == "UTC"


def test_index_to_utc_converts_eastern():
    # pandas uses dateutil/zoneinfo, no pytz required
    idx = pd.date_range("2024-01-01", periods=3, freq="1h", tz="America/New_York")
    result = index_to_utc(idx)
    assert str(result.tz) == "UTC"
    # 00:00 New York (EST = UTC-5) → 05:00 UTC
    assert result[0].hour == 5
