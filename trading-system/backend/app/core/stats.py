"""Map VectorBT stats output to the 9-metric schema (§6.3)."""
import math


def _num(v, default=0.0) -> float:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return default
    if math.isnan(f) or math.isinf(f):
        return default
    return f


def format_stats(vbt_stats) -> dict:
    def g(*keys):
        for k in keys:
            try:
                if k in vbt_stats.index:
                    return vbt_stats[k]
            except (TypeError, AttributeError):
                pass
        return None

    total_return = _num(g("Total Return [%]")) / 100.0
    win_rate = _num(g("Win Rate [%]")) / 100.0
    max_dd = _num(g("Max Drawdown [%]")) / 100.0
    return {
        "total_return": total_return,
        "cagr": _num(g("Annualized Return [%]", "CAGR [%]")) / 100.0,
        "sharpe": _num(g("Sharpe Ratio")),
        "sortino": _num(g("Sortino Ratio")),
        "calmar": _num(g("Calmar Ratio")),
        "max_drawdown": -abs(max_dd),
        "win_rate": win_rate,
        "profit_factor": _num(g("Profit Factor")),
        "trade_count": int(_num(g("Total Trades", "# Trades"))),
    }
