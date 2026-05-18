from typing import Any

from pydantic import BaseModel, Field


class ParamSchema(BaseModel):
    name: str
    type: str = Field(pattern=r"^(int|float|bool)$")
    default: Any
    min: float | None = None
    max: float | None = None


class OutputSchema(BaseModel):
    outputs: list[str]


class IndicatorCreate(BaseModel):
    name: str
    code: str
    language: str = "python"
    params_schema: list[ParamSchema] = []
    output_schema: OutputSchema


class IndicatorRead(BaseModel):
    id: str
    user_id: str
    name: str
    code: str
    language: str
    params_schema: list[Any]
    output_schema: dict
    is_builtin: bool
    created_at: str


class ComputeRequest(BaseModel):
    symbol: str
    exchange: str = Field(pattern=r"^(binance|yfinance)$")
    timeframe: str = Field(pattern=r"^(1m|5m|15m|1h|4h|1d|1w)$")
    from_: str = Field(alias="from")
    to: str
    params: dict = {}

    model_config = {"populate_by_name": True}
