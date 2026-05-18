from pydantic import BaseModel, Field


class Candle(BaseModel):
    open_time: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class CandlesResponse(BaseModel):
    symbol: str
    exchange: str
    timeframe: str
    candles: list[Candle]


TIMEFRAME_PATTERN = r"^(1m|5m|15m|1h|4h|1d|1w)$"
SYMBOL_PATTERN = r"^[A-Z0-9]{1,20}$"


class CandleQuery(BaseModel):
    symbol: str = Field(pattern=SYMBOL_PATTERN)
    exchange: str = Field(pattern=r"^(binance|yfinance)$")
    timeframe: str = Field(pattern=TIMEFRAME_PATTERN)
    from_: str = Field(alias="from")
    to: str
