"""POST /api/v1/evaluate — score an answer against a rubric via the Quality Judge."""

from fastapi import APIRouter

from app.schemas.requests import EvaluateRequest
from app.schemas.responses import EvaluateResponse
from app.services import judge

router = APIRouter()


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(req: EvaluateRequest):
    quality = judge.evaluate(question=req.question, answer=req.answer, rubric=req.rubric)
    return EvaluateResponse(quality=quality)
