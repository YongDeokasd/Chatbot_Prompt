from pydantic import BaseModel, Field


class BenchmarkCreate(BaseModel):
    symbol: str
    exchange: str = Field(pattern=r"^(binance|yfinance)$")


class BenchmarkRead(BaseModel):
    id: str
    symbol: str
    exchange: str
    active: bool
    created_at: str
