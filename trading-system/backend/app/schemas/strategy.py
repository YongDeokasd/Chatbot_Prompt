"""Strategy config models (§6.1)."""
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

ExpressionType = Literal["indicator", "constant", "price"]
PriceSource = Literal["open", "high", "low", "close", "volume"]
Operator = Literal[
    ">", "<", ">=", "<=", "==", "cross_above", "cross_below"
]


class IndicatorExpression(BaseModel):
    type: Literal["indicator"] = "indicator"
    indicator_id: str
    output_key: str
    shift: int = 0


class ConstantExpression(BaseModel):
    type: Literal["constant"] = "constant"
    value: float


class PriceExpression(BaseModel):
    type: Literal["price"] = "price"
    source: PriceSource
    shift: int = 0


Expression = Annotated[
    Union[IndicatorExpression, ConstantExpression, PriceExpression],
    Field(discriminator="type"),
]


class Condition(BaseModel):
    left: Expression
    operator: Operator
    right: Expression


class StrategyConfig(BaseModel):
    entry_conditions: list[Condition] = []
    entry_logic: Literal["AND", "OR"] = "AND"
    exit_conditions: list[Condition] = []
    exit_logic: Literal["AND", "OR"] = "AND"


class StrategyCreate(BaseModel):
    name: str
    symbol: str
    exchange: str = Field(pattern=r"^(binance|yfinance)$")
    timeframe: str = Field(pattern=r"^(1m|5m|15m|1h|4h|1d|1w)$")
    position_type: str = "long"
    fees_bps: float = 10
    slippage_bps: float = 5
    initial_cash: float = 10000
    config: StrategyConfig


class StrategyRead(BaseModel):
    id: str
    user_id: str
    name: str
    symbol: str
    exchange: str
    timeframe: str
    position_type: str
    fees_bps: float
    slippage_bps: float
    initial_cash: float
    config: StrategyConfig
    created_at: str
