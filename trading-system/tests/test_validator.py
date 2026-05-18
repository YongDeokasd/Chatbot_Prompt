"""Unit tests for code static validator (M3/M8 §9.2, §13.1)."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from app.services.indicators.validator import validate_code

VALID_CODE = """
def compute(candles, params):
    import pandas as pd
    length = int(params.get('length', 20))
    return {'value': candles['close'].rolling(length).mean()}
"""

def test_valid_code_passes():
    validate_code(VALID_CODE)

def test_missing_compute_signature_fails():
    with pytest.raises(ValueError, match="compute"):
        validate_code("def run(x): return x")

def test_banned_import_fails():
    with pytest.raises(ValueError, match="(?i)import"):
        validate_code("import socket\ndef compute(candles, params): return {}")

def test_banned_call_exec_fails():
    with pytest.raises(ValueError, match="exec"):
        validate_code("def compute(candles, params): exec('x=1')\n")

def test_banned_call_eval_fails():
    with pytest.raises(ValueError, match="eval"):
        validate_code("def compute(candles, params): return eval('1+1')")

def test_banned_call_open_fails():
    with pytest.raises(ValueError, match="open"):
        validate_code("def compute(candles, params): open('/etc/passwd')\n")

def test_code_too_long_fails():
    code = "def compute(candles, params):\n    x = 1\n" + "#" * 11000
    with pytest.raises(ValueError, match="10KB"):
        validate_code(code)
