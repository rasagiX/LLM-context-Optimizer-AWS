"""
POST /api/v1/run — run a task through the baseline and/or optimized pipeline.
GET  /api/v1/runs/{run_id} — fetch a previous run's results.
"""

import uuid

from fastapi import APIRouter, HTTPException

from app.optimizer.pipeline import OptimizerContext, run as run_pipeline
from app.optimizer.token_utils import count_tokens
from app.schemas.requests import RunRequest
from app.schemas.responses import ComparisonSummary, PipelineResult, RunResponse
from app.services import bedrock, judge, store
from app.services.bedrock import BedrockError

router = APIRouter()


def _build_prompt(question: str, conversation: list[dict], documents: list[dict]) -> str:
    parts = []
    if documents:
        docs_text = "\n\n".join(
            f"[Document {d.get('id', i)}]\n{d.get('content', '')}"
            for i, d in enumerate(documents)
        )
        parts.append(f"Context documents:\n{docs_text}")
    if conversation:
        convo_text = "\n".join(
            f"{m.get('role')}: {m.get('content')}" for m in conversation
        )
        parts.append(f"Conversation history:\n{convo_text}")
    parts.append(f"Question:\n{question}")
    return "\n\n".join(parts)


def _run_pipeline_variant(
    question: str,
    conversation: list[dict],
    documents: list[dict],
    tools: list[dict],
) -> PipelineResult:
    prompt = _build_prompt(question, conversation, documents)
    # BedrockError propagates to the caller (run()) which translates it to HTTPException.
    llm_result = bedrock.invoke(prompt=prompt)

    input_tokens = llm_result.input_tokens or count_tokens(prompt)
    output_tokens = llm_result.output_tokens
    total_tokens = input_tokens + output_tokens

    return PipelineResult(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        latency_ms=llm_result.latency_ms,
        cost=llm_result.cost,
        answer=llm_result.text,
    )


@router.post("/run", response_model=RunResponse)
async def run(req: RunRequest):
    if not req.question:
        raise HTTPException(status_code=400, detail="question is required")

    conversation = [m.model_dump() for m in req.conversation]
    documents = [d.model_dump() for d in req.documents]
    tools = [t.model_dump() for t in req.tools]

    run_id = f"run_{uuid.uuid4().hex[:12]}"

    baseline_result = None
    optimized_result = None
    quality_baseline = None
    quality_optimized = None

    try:
        if req.mode in ("baseline", "compare"):
            baseline_result = _run_pipeline_variant(req.question, conversation, documents, tools)
            if req.rubric:
                quality_baseline = judge.evaluate(
                    req.question, baseline_result.answer, req.rubric
                ).score

        if req.mode in ("optimized", "compare"):
            ctx = OptimizerContext(
                question=req.question,
                conversation=conversation,
                documents=documents,
                tools=tools,
            )
            optimized_ctx = run_pipeline(ctx).context
            optimized_result = _run_pipeline_variant(
                optimized_ctx.question,
                optimized_ctx.conversation,
                optimized_ctx.documents,
                optimized_ctx.tools,
            )
            if req.rubric:
                quality_optimized = judge.evaluate(
                    req.question, optimized_result.answer, req.rubric
                ).score

    except BedrockError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    comparison = None
    if baseline_result and optimized_result:
        token_reduction = None
        if baseline_result.input_tokens > 0:
            token_reduction = round(
                (1 - optimized_result.input_tokens / baseline_result.input_tokens) * 100, 2
            )

        cost_reduction = None
        if baseline_result.cost and baseline_result.cost > 0:
            cost_reduction = round(
                (1 - optimized_result.cost / baseline_result.cost) * 100, 2
            )

        latency_reduction = None
        if baseline_result.latency_ms > 0:
            latency_reduction = round(
                (1 - optimized_result.latency_ms / baseline_result.latency_ms) * 100, 2
            )

        comparison = ComparisonSummary(
            token_reduction_percent=token_reduction,
            cost_reduction_percent=cost_reduction,
            latency_reduction_percent=latency_reduction,
            quality_baseline=quality_baseline,
            quality_optimized=quality_optimized,
        )

    response = RunResponse(
        run_id=run_id,
        baseline=baseline_result,
        optimized=optimized_result,
        comparison=comparison,
    )

    store.save_run(run_id, response.model_dump())
    return response


@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run(run_id: str):
    data = store.get_run(run_id)
    if data is None:
        raise HTTPException(status_code=404, detail="run not found")
    return data
