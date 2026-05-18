"""Vectorized signal evaluation (§6.2)."""
from dataclasses import dataclass

import pandas as pd


@dataclass
class EvalContext:
    candles: pd.DataFrame  # cols: open/high/low/close/volume, DatetimeIndex
    indicators: dict[str, dict[str, pd.Series]]  # indicator_id -> key -> series


def evaluate(expr: dict, ctx: EvalContext) -> pd.Series:
    etype = expr["type"]
    if etype == "constant":
        return pd.Series(float(expr["value"]), index=ctx.candles.index)
    if etype == "price":
        s = ctx.candles[expr["source"]].astype(float)
        shift = int(expr.get("shift", 0))
        return s.shift(shift) if shift else s
    if etype == "indicator":
        ind = ctx.indicators.get(expr["indicator_id"], {})
        if expr["output_key"] not in ind:
            raise ValueError(
                f"Indicator {expr['indicator_id']} missing output "
                f"{expr['output_key']}"
            )
        s = ind[expr["output_key"]]
        shift = int(expr.get("shift", 0))
        return s.shift(shift) if shift else s
    raise ValueError(f"Unknown expression type: {etype}")


def cross_above(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a > b) & (a.shift(1) <= b.shift(1))


def cross_below(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a < b) & (a.shift(1) >= b.shift(1))


_OPS = {
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
    "cross_above": cross_above,
    "cross_below": cross_below,
}


def eval_condition(condition: dict, ctx: EvalContext) -> pd.Series:
    left = evaluate(condition["left"], ctx)
    right = evaluate(condition["right"], ctx)
    op = condition["operator"]
    fn = _OPS.get(op)
    if fn is None:
        raise ValueError(f"Unknown operator: {op}")
    return fn(left, right).fillna(False).astype(bool)


def eval_logic(conditions: list[dict], logic: str,
                ctx: EvalContext) -> pd.Series:
    if not conditions:
        return pd.Series(False, index=ctx.candles.index)
    series = [eval_condition(c, ctx) for c in conditions]
    acc = series[0]
    for s in series[1:]:
        acc = (acc & s) if logic == "AND" else (acc | s)
    return acc.fillna(False).astype(bool)
