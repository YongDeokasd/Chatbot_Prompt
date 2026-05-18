"""Backtest engine: fetch, compute indicators, signals, vectorbt (§6)."""
import time
import uuid

import pandas as pd

from app.core.stats import format_stats
from app.core.time import iso_z, parse_iso
from app.db import SessionLocal
from app.models import Indicator
from app.services.backtest.signal_evaluator import EvalContext, eval_logic
from app.services.indicators.builtin import BUILTIN_NAMES, compute_builtin
from app.services.indicators.sandbox import run_in_sandbox
from app.services.market.service import get_candles

_TF_SECS = {
    "1m": 60, "5m": 300, "15m": 900, "1h": 3600,
    "4h": 14400, "1d": 86400, "1w": 604800,
}
_TF_FREQ = {
    "1m": "1min", "5m": "5min", "15m": "15min", "1h": "1h",
    "4h": "4h", "1d": "1D", "1w": "1W",
}


def _collect_indicator_refs(config: dict) -> set[str]:
    refs: set[str] = set()
    for grp in ("entry_conditions", "exit_conditions"):
        for cond in config.get(grp, []):
            for side in ("left", "right"):
                e = cond.get(side, {})
                if e.get("type") == "indicator":
                    refs.add(e["indicator_id"])
    return refs


async def _compute_indicator(ind_id: str, candles: list[dict],
                              df: pd.DataFrame) -> dict[str, pd.Series]:
    try:
        uid = uuid.UUID(ind_id)
    except ValueError:
        raise ValueError(f"Invalid indicator id: {ind_id}")
    async with SessionLocal() as s:
        row = await s.get(Indicator, uid)
    if row is None:
        raise ValueError(f"Indicator {ind_id} not found")

    if row.is_builtin and row.name.upper() in BUILTIN_NAMES:
        out = compute_builtin(row.name, df, {})
    else:
        result = await run_in_sandbox(row.code, candles, {})
        out = result.get("outputs", result)
    return {k: pd.Series(v, index=df.index, dtype="float64")
            for k, v in out.items()}


async def run_backtest(strategy_read, from_dt, to_dt) -> dict:
    t0 = time.monotonic()
    tf = strategy_read.timeframe
    secs = _TF_SECS[tf]
    span = (parse_iso(to_dt) if isinstance(to_dt, str) else to_dt) - (
        parse_iso(from_dt) if isinstance(from_dt, str) else from_dt
    )
    est = int(span.total_seconds() / secs)
    if est > 100_000:
        raise ValueError(
            f"Estimated {est} candles exceeds 100k limit; narrow the range"
        )

    candles = await get_candles(
        strategy_read.symbol, strategy_read.exchange, tf, from_dt, to_dt
    )
    if not candles:
        raise ValueError("No candle data for the requested range")

    df = pd.DataFrame(candles)
    df.index = pd.DatetimeIndex(
        [parse_iso(c["open_time"]) for c in candles]
    )
    df = df[["open", "high", "low", "close", "volume"]].astype(float)

    config = strategy_read.config.model_dump()
    indicators: dict[str, dict[str, pd.Series]] = {}
    for ind_id in _collect_indicator_refs(config):
        indicators[ind_id] = await _compute_indicator(ind_id, candles, df)

    ctx = EvalContext(candles=df, indicators=indicators)
    entries = eval_logic(
        config["entry_conditions"], config["entry_logic"], ctx
    )
    exits = eval_logic(
        config["exit_conditions"], config["exit_logic"], ctx
    )

    import vectorbt as vbt

    close = df["close"]
    pf = vbt.Portfolio.from_signals(
        close,
        entries.shift(1).fillna(False).astype(bool),
        exits.shift(1).fillna(False).astype(bool),
        fees=float(strategy_read.fees_bps) / 10_000.0,
        slippage=float(strategy_read.slippage_bps) / 10_000.0,
        init_cash=float(strategy_read.initial_cash),
        freq=_TF_FREQ.get(tf, "1D"),
    )

    stats = format_stats(pf.stats())

    trades: list[dict] = []
    try:
        trec = pf.trades.records_readable
        for _, r in trec.iterrows():
            etime = r.get("Entry Timestamp")
            xtime = r.get("Exit Timestamp")
            trades.append({
                "entry_time": iso_z(pd.Timestamp(etime).to_pydatetime()),
                "entry_price": float(r.get("Avg Entry Price", 0.0)),
                "exit_time": (
                    iso_z(pd.Timestamp(xtime).to_pydatetime())
                    if pd.notna(xtime) else None
                ),
                "exit_price": (
                    float(r.get("Avg Exit Price"))
                    if pd.notna(r.get("Avg Exit Price")) else None
                ),
                "size": float(r.get("Size", 0.0)),
                "pnl": float(r.get("PnL", 0.0)),
                "return_pct": float(r.get("Return", 0.0)),
                "reason": str(r.get("Status", "")),
            })
    except Exception:
        trades = []

    equity_curve: list[dict] = []
    try:
        ev = pf.value()
        for ts, val in ev.items():
            equity_curve.append({
                "time": iso_z(pd.Timestamp(ts).to_pydatetime()),
                "value": float(val),
            })
    except Exception:
        equity_curve = []

    duration_ms = int((time.monotonic() - t0) * 1000)
    return {
        "stats": stats,
        "trades": trades,
        "equity_curve": equity_curve,
        "duration_ms": duration_ms,
    }
