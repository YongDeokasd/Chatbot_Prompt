"""Strategy CRUD (§6)."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_token
from app.core.time import iso_z
from app.db import get_session
from app.models import Strategy
from app.schemas.strategy import StrategyConfig, StrategyCreate, StrategyRead

router = APIRouter(prefix="/api/strategies", tags=["strategies"],
                   dependencies=[Depends(require_token)])


def _to_read(row: Strategy) -> StrategyRead:
    return StrategyRead(
        id=str(row.id),
        user_id=row.user_id,
        name=row.name,
        symbol=row.symbol,
        exchange=row.exchange,
        timeframe=row.timeframe,
        position_type=row.position_type,
        fees_bps=float(row.fees_bps),
        slippage_bps=float(row.slippage_bps),
        initial_cash=float(row.initial_cash),
        config=StrategyConfig(**row.config_json),
        created_at=iso_z(row.created_at),
    )


async def _get_or_404(s: AsyncSession, sid: str) -> Strategy:
    try:
        u = uuid.UUID(sid)
    except ValueError:
        raise HTTPException(404, "Strategy not found")
    row = await s.get(Strategy, u)
    if row is None:
        raise HTTPException(404, "Strategy not found")
    return row


@router.post("", response_model=StrategyRead, status_code=201)
async def create(body: StrategyCreate, s: AsyncSession = Depends(get_session)):
    row = Strategy(
        user_id="local-user",
        name=body.name,
        symbol=body.symbol,
        exchange=body.exchange,
        timeframe=body.timeframe,
        position_type=body.position_type,
        fees_bps=body.fees_bps,
        slippage_bps=body.slippage_bps,
        initial_cash=body.initial_cash,
        config_json=body.config.model_dump(),
    )
    s.add(row)
    await s.commit()
    await s.refresh(row)
    return _to_read(row)


@router.get("", response_model=list[StrategyRead])
async def list_all(s: AsyncSession = Depends(get_session)):
    rows = (await s.execute(select(Strategy).order_by(Strategy.created_at))).scalars().all()
    return [_to_read(r) for r in rows]


@router.get("/{sid}", response_model=StrategyRead)
async def get_one(sid: str, s: AsyncSession = Depends(get_session)):
    return _to_read(await _get_or_404(s, sid))


@router.put("/{sid}", response_model=StrategyRead)
async def update(sid: str, body: StrategyCreate,
                 s: AsyncSession = Depends(get_session)):
    row = await _get_or_404(s, sid)
    row.name = body.name
    row.symbol = body.symbol
    row.exchange = body.exchange
    row.timeframe = body.timeframe
    row.position_type = body.position_type
    row.fees_bps = body.fees_bps
    row.slippage_bps = body.slippage_bps
    row.initial_cash = body.initial_cash
    row.config_json = body.config.model_dump()
    await s.commit()
    await s.refresh(row)
    return _to_read(row)


@router.delete("/{sid}", status_code=204)
async def delete(sid: str, s: AsyncSession = Depends(get_session)):
    row = await _get_or_404(s, sid)
    await s.delete(row)
    await s.commit()
