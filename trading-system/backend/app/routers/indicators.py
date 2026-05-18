"""Indicator CRUD + compute (§5)."""
import uuid

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_token
from app.core.time import iso_z, parse_iso
from app.db import get_session
from app.models import Indicator
from app.schemas.indicators import ComputeRequest, IndicatorCreate, IndicatorRead
from app.services.indicators.builtin import BUILTIN_NAMES, compute_builtin
from app.services.indicators.sandbox import run_in_sandbox
from app.services.indicators.validator import validate_code
from app.services.market.service import get_candles

router = APIRouter(prefix="/api/indicators", tags=["indicators"],
                   dependencies=[Depends(require_token)])


def _to_read(row: Indicator) -> IndicatorRead:
    return IndicatorRead(
        id=str(row.id),
        user_id=row.user_id,
        name=row.name,
        code=row.code,
        language=row.language,
        params_schema=row.params_schema or [],
        output_schema=row.output_schema or {"outputs": []},
        is_builtin=row.is_builtin,
        created_at=iso_z(row.created_at),
    )


async def _get_or_404(s: AsyncSession, ind_id: str) -> Indicator:
    try:
        uid = uuid.UUID(ind_id)
    except ValueError:
        raise HTTPException(404, "Indicator not found")
    row = await s.get(Indicator, uid)
    if row is None:
        raise HTTPException(404, "Indicator not found")
    return row


@router.post("", response_model=IndicatorRead, status_code=201)
async def create(body: IndicatorCreate, s: AsyncSession = Depends(get_session)):
    try:
        validate_code(body.code)
    except ValueError as e:
        raise HTTPException(422, str(e))
    row = Indicator(
        user_id="local-user",
        name=body.name,
        code=body.code,
        language=body.language,
        params_schema=[p.model_dump() for p in body.params_schema],
        output_schema=body.output_schema.model_dump(),
        is_builtin=False,
    )
    s.add(row)
    await s.commit()
    await s.refresh(row)
    return _to_read(row)


@router.get("", response_model=list[IndicatorRead])
async def list_all(s: AsyncSession = Depends(get_session)):
    rows = (await s.execute(select(Indicator).order_by(Indicator.created_at))).scalars().all()
    return [_to_read(r) for r in rows]


@router.get("/{ind_id}", response_model=IndicatorRead)
async def get_one(ind_id: str, s: AsyncSession = Depends(get_session)):
    return _to_read(await _get_or_404(s, ind_id))


@router.put("/{ind_id}", response_model=IndicatorRead)
async def update(ind_id: str, body: IndicatorCreate,
                 s: AsyncSession = Depends(get_session)):
    row = await _get_or_404(s, ind_id)
    if row.is_builtin:
        raise HTTPException(422, "Cannot modify builtin indicator")
    try:
        validate_code(body.code)
    except ValueError as e:
        raise HTTPException(422, str(e))
    row.name = body.name
    row.code = body.code
    row.language = body.language
    row.params_schema = [p.model_dump() for p in body.params_schema]
    row.output_schema = body.output_schema.model_dump()
    await s.commit()
    await s.refresh(row)
    return _to_read(row)


@router.delete("/{ind_id}", status_code=204)
async def delete(ind_id: str, s: AsyncSession = Depends(get_session)):
    row = await _get_or_404(s, ind_id)
    if row.is_builtin:
        raise HTTPException(422, "Cannot delete builtin indicator")
    await s.delete(row)
    await s.commit()


@router.post("/{ind_id}/compute")
async def compute(ind_id: str, body: ComputeRequest,
                  s: AsyncSession = Depends(get_session)):
    row = await _get_or_404(s, ind_id)
    start, end = parse_iso(body.from_), parse_iso(body.to)
    if start >= end:
        raise HTTPException(422, "`from` must be before `to`")
    try:
        candles = await get_candles(
            body.symbol, body.exchange, body.timeframe, start, end
        )
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not candles:
        return {"times": [], "outputs": {}}

    times = [c["open_time"] for c in candles]
    if row.is_builtin and row.name.upper() in BUILTIN_NAMES:
        df = pd.DataFrame(candles)
        outputs = compute_builtin(row.name, df, body.params)
    else:
        try:
            result = await run_in_sandbox(row.code, candles, body.params)
        except (TimeoutError, RuntimeError) as e:
            raise HTTPException(422, f"Sandbox error: {e}")
        outputs = result.get("outputs", result)
    return {"times": times, "outputs": outputs}
