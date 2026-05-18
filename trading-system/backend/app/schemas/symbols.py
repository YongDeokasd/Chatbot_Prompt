from pydantic import BaseModel


class SymbolResult(BaseModel):
    symbol: str
    exchange: str
    name: str | None = None


class TimeframeInfo(BaseModel):
    timeframe: str
    available: bool
    max_days: int | None = None


class TimeframesResponse(BaseModel):
    symbol: str
    exchange: str
    timeframes: list[TimeframeInfo]
