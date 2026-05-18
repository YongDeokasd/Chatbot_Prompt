"""AI Pine -> Python conversion endpoint (§10)."""
import json

from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_token
from app.schemas.ai import PineConvertRequest, PineConvertResponse
from app.services.indicators.ai_converter import convert_pine_to_python

router = APIRouter(prefix="/api/ai", tags=["ai"],
                   dependencies=[Depends(require_token)])


@router.post("/convert-pine", response_model=PineConvertResponse)
async def convert_pine(body: PineConvertRequest):
    try:
        result = await convert_pine_to_python(body.pine_code)
    except ValueError as e:
        msg = str(e)
        try:
            payload = json.loads(msg)
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict) and "unsupported_tokens" in payload:
            raise HTTPException(
                422,
                detail={
                    "message": "Pine script uses unsupported features",
                    "unsupported_tokens": payload["unsupported_tokens"],
                },
            )
        raise HTTPException(422, detail=msg)
    return PineConvertResponse(**result)
