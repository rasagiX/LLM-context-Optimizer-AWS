"""POST /api/v1/evaluate — score an answer against a rubric via the Quality Judge."""

from fastapi import APIRouter, HTTPException

from app.schemas.requests import EvaluateRequest
from app.schemas.responses import EvaluateResponse
from app.services import judge
from app.services.bedrock import BedrockError

router = APIRouter()


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(req: EvaluateRequest):
    try:
        quality = judge.evaluate(question=req.question, answer=req.answer, rubric=req.rubric)
    except BedrockError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return EvaluateResponse(quality=quality)
