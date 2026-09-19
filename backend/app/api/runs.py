"""
POST /api/v1/run — run a task through the baseline and/or optimized pipeline.
GET  /api/v1/runs/{run_id} — fetch a previous run's results.
"""

import uuid

import botocore.exceptions
from fastapi import APIRouter, HTTPException

from app.optimizer.pipeline import OptimizerContext, run as run_pipeline
from app.optimizer.token_utils import count_tokens
from app.schemas.requests import RunRequest
from app.schemas.responses import ComparisonSummary, PipelineResult, RunResponse
from app.services import bedrock, judge, store

router = APIRouter()

# ---------------------------------------------------------------------------
# Pricing table (USD per 1 000 tokens, as of 2024-11)
# Update here if AWS changes pricing or you swap models.
# ---------------------------------------------------------------------------
_PRICING = {
    # Claude 3.5 Sonnet v2
    "anthropic.claude-3-5-sonnet-20241022-v2:0": {"input": 0.003, "output": 0.015},
    # Claude 3.5 Haiku
    "anthropic.claude-3-5-haiku-20241022-v1:0":  {"input": 0.001, "output": 0.005},
    # Claude 3 Sonnet
    "anthropic.claude-3-sonnet-20240229-v1:0":   {"input": 0.003, "output": 0.015},
    # Claude 3 Haiku
    "anthropic.claude-3-haiku-20240307-v1:0":    {"input": 0.00025, "output": 0.00125},
}

import os
_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")


def _compute_cost(input_tokens: int, output_tokens: int) -> float:
    """Return estimated USD cost for a single Bedrock call."""
    pricing = _PRICING.get(_MODEL_ID, {"input": 0.003, "output": 0.015})
    return round(
        (input_tokens  / 1000) * pricing["input"] +
        (output_tokens / 1000) * pricing["output"],
        6,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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
    """
    Build a prompt and call Bedrock. Raises HTTPException(503) on any
    AWS / credential error so the API returns a clean JSON error rather
    than a raw boto3 traceback.
    """
    prompt = _build_prompt(question, conversation, documents)

    try:
        llm_result = bedrock.invoke(prompt=prompt)
    except botocore.exceptions.NoCredentialsError:
        raise HTTPException(
            status_code=503,
            detail=(
                "AWS credentials not configured. "
                "Fill in AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in backend/.env "
                "and restart the server."
            ),
        )
    except botocore.exceptions.ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "Unknown")
        raise HTTPException(
            status_code=503,
            detail=f"Bedrock API error ({code}): {exc.response['Error'].get('Message', str(exc))}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"LLM call failed: {str(exc)}",
        )

    input_tokens  = llm_result.input_tokens or count_tokens(prompt)
    output_tokens = llm_result.output_tokens
    cost          = _compute_cost(input_tokens, output_tokens)

    return PipelineResult(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        latency_ms=llm_result.latency_ms,
        cost=cost,
        answer=llm_result.text,
    )


def _safe_judge(question: str, answer: str, rubric: list[str]) -> float | None:
    """
    Run the quality judge and return a float score.
    Returns None (instead of crashing) if Bedrock is unavailable.
    """
    try:
        return judge.evaluate(question, answer, rubric).score
    except botocore.exceptions.NoCredentialsError:
        return None
    except botocore.exceptions.ClientError:
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------

@router.post("/run", response_model=RunResponse)
async def run(req: RunRequest):
    if not req.question:
        raise HTTPException(status_code=400, detail="question is required")

    conversation = [m.model_dump() for m in req.conversation]
    documents    = [d.model_dump() for d in req.documents]
    tools        = [t.model_dump() for t in req.tools]

    run_id = f"run_{uuid.uuid4().hex[:12]}"

    baseline_result   = None
    optimized_result  = None
    quality_baseline  = None
    quality_optimized = None

    if req.mode in ("baseline", "compare"):
        baseline_result = _run_pipeline_variant(req.question, conversation, documents, tools)
        if req.rubric:
            quality_baseline = _safe_judge(req.question, baseline_result.answer, req.rubric)

    if req.mode in ("optimized", "compare"):
        ctx = OptimizerContext(
            question=req.question,
            conversation=conversation,
            documents=documents,
            tools=tools,
        )
        optimized_ctx    = run_pipeline(ctx).context
        optimized_result = _run_pipeline_variant(
            optimized_ctx.question,
            optimized_ctx.conversation,
            optimized_ctx.documents,
            optimized_ctx.tools,
        )
        if req.rubric:
            quality_optimized = _safe_judge(req.question, optimized_result.answer, req.rubric)

    comparison = None
    if baseline_result and optimized_result:
        token_reduction = None
        if baseline_result.input_tokens > 0:
            token_reduction = round(
                (1 - optimized_result.input_tokens / baseline_result.input_tokens) * 100, 2
            )
        cost_reduction = None
        if baseline_result.cost > 0:
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
