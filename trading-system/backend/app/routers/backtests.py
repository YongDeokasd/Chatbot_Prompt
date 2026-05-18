"""Backtest run + retrieval (§6.3)."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_token
from app.core.time import iso_z, parse_iso
from app.db import get_session
from app.models import BacktestResult, Strategy
from app.routers.strategies import _to_read as strategy_to_read
from app.schemas.backtest import (
    BacktestListItem,
    BacktestResponse,
    BacktestRunRequest,
)
from app.services.backtest.engine import run_backtest

router = APIRouter(prefix="/api/backtests", tags=["backtests"],
                   dependencies=[Depends(require_token)])


@router.post("/run", response_model=BacktestResponse)
async def run(body: BacktestRunRequest, s: AsyncSession = Depends(get_session)):
    try:
        sid = uuid.UUID(body.strategy_id)
    except ValueError:
        raise HTTPException(404, "Strategy not found")
    strat = await s.get(Strategy, sid)
    if strat is None:
        raise HTTPException(404, "Strategy not found")

    start, end = parse_iso(body.from_), parse_iso(body.to)
    if start >= end:
        raise HTTPException(422, "`from` must be before `to`")

    strategy_read = strategy_to_read(strat)
    try:
        result = await run_backtest(strategy_read, start, end)
    except ValueError as e:
        raise HTTPException(422, str(e))

    row = BacktestResult(
        strategy_id=sid,
        period_from=start,
        period_to=end,
        stats_json=result["stats"],
        trades_json={"trades": result["trades"]},
        equity_curve_json={"equity_curve": result["equity_curve"]},
        duration_ms=result["duration_ms"],
    )
    s.add(row)
    await s.commit()
    await s.refresh(row)

    return BacktestResponse(
        id=str(row.id),
        duration_ms=result["duration_ms"],
        stats=result["stats"],
        trades=result["trades"],
        equity_curve=result["equity_curve"],
    )


@router.get("", response_model=list[BacktestListItem])
async def list_all(s: AsyncSession = Depends(get_session)):
    rows = (
        await s.execute(
            select(BacktestResult).order_by(BacktestResult.created_at.desc())
        )
    ).scalars().all()
    return [
        BacktestListItem(
            id=str(r.id),
            strategy_id=str(r.strategy_id),
            period_from=iso_z(r.period_from),
            period_to=iso_z(r.period_to),
            stats=r.stats_json,
            created_at=iso_z(r.created_at),
        )
        for r in rows
    ]


@router.get("/{bid}", response_model=BacktestResponse)
async def get_one(bid: str, s: AsyncSession = Depends(get_session)):
    try:
        u = uuid.UUID(bid)
    except ValueError:
        raise HTTPException(404, "Backtest not found")
    r = await s.get(BacktestResult, u)
    if r is None:
        raise HTTPException(404, "Backtest not found")
    return BacktestResponse(
        id=str(r.id),
        duration_ms=r.duration_ms,
        stats=r.stats_json,
        trades=r.trades_json.get("trades", []),
        equity_curve=r.equity_curve_json.get("equity_curve", []),
    )
