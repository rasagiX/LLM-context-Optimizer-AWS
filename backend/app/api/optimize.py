"""POST /api/v1/optimize — run the Context Compiler without calling the LLM."""

from fastapi import APIRouter

from app.optimizer.pipeline import OptimizerContext, run as run_pipeline
from app.optimizer.token_utils import count_context_tokens
from app.schemas.requests import OptimizeRequest
from app.schemas.responses import OptimizeResponse

router = APIRouter()


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize(req: OptimizeRequest):
    original_tokens = count_context_tokens(
        question=req.question or "",
        conversation=[m.model_dump() for m in req.conversation],
        documents=[d.model_dump() for d in req.documents],
        tools=[t.model_dump() for t in req.tools],
    )

    ctx = OptimizerContext(
        question=req.question or "",
        conversation=[m.model_dump() for m in req.conversation],
        documents=[d.model_dump() for d in req.documents],
        tools=[t.model_dump() for t in req.tools],
    )
    result = run_pipeline(ctx)

    optimized_tokens = count_context_tokens(
        question=result.context.question,
        conversation=result.context.conversation,
        documents=result.context.documents,
        tools=result.context.tools,
    )

    reduction = 0.0
    if original_tokens > 0:
        reduction = round((1 - optimized_tokens / original_tokens) * 100, 2)

    return OptimizeResponse(
        optimized_context={
            "question": result.context.question,
            "conversation": result.context.conversation,
            "documents": result.context.documents,
            "tools": result.context.tools,
        },
        original_tokens=original_tokens,
        optimized_tokens=optimized_tokens,
        reduction_percent=reduction,
        steps_applied=result.steps_applied,
    )
