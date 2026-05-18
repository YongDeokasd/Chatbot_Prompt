"""Benchmark symbol CRUD (§11)."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_token
from app.core.time import iso_z
from app.db import get_session
from app.models import BenchmarkSymbol
from app.schemas.benchmark import BenchmarkCreate, BenchmarkRead

router = APIRouter(prefix="/api/benchmarks", tags=["benchmarks"],
                   dependencies=[Depends(require_token)])


def _to_read(r: BenchmarkSymbol) -> BenchmarkRead:
    return BenchmarkRead(
        id=str(r.id),
        symbol=r.symbol,
        exchange=r.exchange,
        active=r.active,
        created_at=iso_z(r.created_at),
    )


@router.post("", response_model=BenchmarkRead, status_code=201)
async def create(body: BenchmarkCreate, s: AsyncSession = Depends(get_session)):
    row = BenchmarkSymbol(
        user_id="local-user",
        symbol=body.symbol,
        exchange=body.exchange,
        active=True,
    )
    s.add(row)
    try:
        await s.commit()
    except IntegrityError:
        await s.rollback()
        raise HTTPException(409, "Benchmark already exists")
    await s.refresh(row)
    return _to_read(row)


@router.get("", response_model=list[BenchmarkRead])
async def list_all(s: AsyncSession = Depends(get_session)):
    rows = (await s.execute(
        select(BenchmarkSymbol).order_by(BenchmarkSymbol.created_at)
    )).scalars().all()
    return [_to_read(r) for r in rows]


@router.delete("/{bid}", status_code=204)
async def delete(bid: str, s: AsyncSession = Depends(get_session)):
    try:
        u = uuid.UUID(bid)
    except ValueError:
        raise HTTPException(404, "Benchmark not found")
    row = await s.get(BenchmarkSymbol, u)
    if row is None:
        raise HTTPException(404, "Benchmark not found")
    await s.delete(row)
    await s.commit()
