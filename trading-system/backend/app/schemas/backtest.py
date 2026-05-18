from pydantic import BaseModel, Field


class BacktestRunRequest(BaseModel):
    strategy_id: str
    from_: str = Field(alias="from")
    to: str

    model_config = {"populate_by_name": True}


class TradeRecord(BaseModel):
    entry_time: str
    entry_price: float
    exit_time: str | None = None
    exit_price: float | None = None
    size: float
    pnl: float
    return_pct: float
    reason: str


class EquityPoint(BaseModel):
    time: str
    value: float


class BacktestStats(BaseModel):
    total_return: float
    cagr: float
    sharpe: float
    sortino: float
    calmar: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    trade_count: int


class BacktestResponse(BaseModel):
    id: str
    duration_ms: int
    stats: BacktestStats
    trades: list[TradeRecord]
    equity_curve: list[EquityPoint]


class BacktestListItem(BaseModel):
    id: str
    strategy_id: str
    period_from: str
    period_to: str
    stats: BacktestStats
    created_at: str
