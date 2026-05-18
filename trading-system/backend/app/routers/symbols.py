import re

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import require_token
from app.schemas.symbols import SymbolResult, TimeframeInfo, TimeframesResponse
from app.services.market.service import get_available_timeframes

router = APIRouter(prefix="/api/symbols", tags=["symbols"])

_CRYPTO = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "DOTUSDT", "MATICUSDT",
]
_STOCK_RE = re.compile(r"^[A-Z\^\.]{1,10}$")


@router.get("/search", response_model=list[SymbolResult],
            dependencies=[Depends(require_token)])
async def search(
    q: str = Query(min_length=1, max_length=20),
    category: str = Query(pattern=r"^(crypto|stocks|index)$"),
):
    qu = q.upper()
    if category == "crypto":
        return [
            SymbolResult(symbol=s, exchange="binance", name=s)
            for s in _CRYPTO
            if qu in s
        ]
    if _STOCK_RE.match(qu):
        return [SymbolResult(symbol=qu, exchange="yfinance", name=qu)]
    return []


@router.get("/{symbol}/timeframes", response_model=TimeframesResponse,
            dependencies=[Depends(require_token)])
async def timeframes(
    symbol: str,
    exchange: str = Query(pattern=r"^(binance|yfinance)$"),
):
    try:
        infos = get_available_timeframes(exchange)
    except ValueError as e:
        raise HTTPException(422, str(e))
    return TimeframesResponse(
        symbol=symbol,
        exchange=exchange,
        timeframes=[TimeframeInfo(**i) for i in infos],
    )
