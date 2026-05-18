from typing import Any

from pydantic import BaseModel, Field


class PineConvertRequest(BaseModel):
    pine_code: str = Field(max_length=20480)


class PineConvertResponse(BaseModel):
    python_code: str
    params_schema: list[Any] = []
    output_schema: dict = {"outputs": []}
    explanation: str = ""
    warnings: list[str] = []
