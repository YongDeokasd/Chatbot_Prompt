from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import require_token
from app.core.time import parse_iso
from app.schemas.market import CandlesResponse
from app.services.market import binance
from app.services.market.service import get_candles as svc_get_candles

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/candles", response_model=CandlesResponse, dependencies=[Depends(require_token)])
async def get_candles(
    symbol: str = Query(pattern=r"^[A-Z0-9\^\.]{1,20}$"),
    exchange: str = Query(pattern=r"^(binance|yfinance)$"),
    timeframe: str = Query(pattern=r"^(1m|5m|15m|1h|4h|1d|1w)$"),
    from_: str = Query(alias="from"),
    to: str = Query(),
):
    start, end = parse_iso(from_), parse_iso(to)
    if start >= end:
        raise HTTPException(422, "`from` must be before `to`")

    try:
        if exchange == "binance":
            candles = await binance.fetch_candles(symbol, timeframe, start, end)
        else:
            candles = await svc_get_candles(
                symbol, exchange, timeframe, start, end
            )
    except ValueError as e:
        raise HTTPException(422, str(e))

    return CandlesResponse(
        symbol=symbol, exchange=exchange, timeframe=timeframe, candles=candles
    )
