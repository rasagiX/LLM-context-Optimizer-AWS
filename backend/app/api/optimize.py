"""
POST /api/v1/optimize  — run the Context Compiler without calling the LLM.
GET  /api/v1/optimize/demo — zero-argument demo that shows all 5 optimizer
                             steps firing on a realistic mixed-noise payload.
                             Perfect for live demos and smoke-testing.
"""

from fastapi import APIRouter

from app.optimizer.pipeline import OptimizerContext, run as run_pipeline
from app.optimizer.token_utils import count_context_tokens
from app.schemas.requests import OptimizeRequest
from app.schemas.responses import OptimizeResponse

router = APIRouter()


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------

import time

from app.services.cloudwatch import log_pipeline_execution

def _run_optimize(
    question: str,
    conversation: list[dict],
    documents: list[dict],
    tools: list[dict],
) -> OptimizeResponse:
    start_time = time.perf_counter()

    original_tokens = count_context_tokens(
        question=question,
        conversation=conversation,
        documents=documents,
        tools=tools,
    )

    ctx = OptimizerContext(
        question=question,
        conversation=conversation,
        documents=documents,
        tools=tools,
    )
    result = run_pipeline(ctx)

    optimized_tokens = count_context_tokens(
        question=result.context.question,
        conversation=result.context.conversation,
        documents=result.context.documents,
        tools=result.context.tools,
    )

    latency_ms = int((time.perf_counter() - start_time) * 1000)
    tokens_saved = max(0, original_tokens - optimized_tokens)

    reduction = 0.0
    if original_tokens > 0:
        reduction = round((1 - optimized_tokens / original_tokens) * 100, 2)

    # Standard Claude 3.5 Sonnet pricing: $0.003 / 1k input tokens
    cost_saved_est = round((tokens_saved / 1000.0) * 0.003, 6)

    log_pipeline_execution(
        endpoint="/api/v1/optimize",
        original_tokens=original_tokens,
        optimized_tokens=optimized_tokens,
        reduction_percent=reduction,
        latency_ms=latency_ms,
        semantic_preservation_score=result.semantic_preservation_score,
    )

    return OptimizeResponse(
        optimized_context={
            "question":      result.context.question,
            "conversation":  result.context.conversation,
            "documents":     result.context.documents,
            "tools":         result.context.tools,
        },
        original_tokens=original_tokens,
        optimized_tokens=optimized_tokens,
        reduction_percent=reduction,
        steps_applied=result.steps_applied,
        tokens_saved=tokens_saved,
        optimization_latency_ms=latency_ms,
        cost_saved_est=cost_saved_est,
        semantic_preservation_score=result.semantic_preservation_score,
    )



# ---------------------------------------------------------------------------
# POST /api/v1/optimize
# ---------------------------------------------------------------------------

@router.post("/optimize", response_model=OptimizeResponse)
async def optimize(req: OptimizeRequest):
    """Run the optimizer pipeline on the provided context. No LLM call."""
    return _run_optimize(
        question=req.question or "",
        conversation=[m.model_dump() for m in req.conversation],
        documents=[d.model_dump() for d in req.documents],
        tools=[t.model_dump() for t in req.tools],
    )


# ---------------------------------------------------------------------------
# GET /api/v1/optimize/demo
# ---------------------------------------------------------------------------

# Pre-built demo payload — exercises all 5 optimizer steps:
#   history_compressor : 12-turn conversation (> 6 kept limit)
#   deduplicator       : 1 exact duplicate + 1 near-duplicate document
#   context_pruner     : 3 irrelevant documents mixed in
#   tool_selector      : 5 tools, only 2 relevant to the question
#   prompt_compressor  : filler phrases in one document

_DEMO_QUESTION = (
    "Based on our discussion and the attached documents, "
    "which cloud provider should we use for the payments service?"
)

_DEMO_CONVERSATION = [
    {"role": "user",      "content": "We need to choose a cloud provider for our payments service."},
    {"role": "assistant", "content": "What are your main requirements?"},
    {"role": "user",      "content": "We must be PCI-DSS compliant for card processing."},
    {"role": "assistant", "content": "AWS, GCP, and Azure all support PCI-DSS workloads."},
    {"role": "user",      "content": "Our customers are in the EU — GDPR data residency is required."},
    {"role": "assistant", "content": "All three have EU regions with GDPR data processing agreements."},
    {"role": "user",      "content": "Our engineering team has 8 AWS certifications and deep AWS experience."},
    {"role": "assistant", "content": "That makes AWS the path of least resistance operationally."},
    {"role": "user",      "content": "We also need SOC 2 Type II for our enterprise contracts."},
    {"role": "assistant", "content": "AWS is SOC 2 Type II certified across its core services."},
    {"role": "user",      "content": "Budget-wise we want pay-as-you-go, no large upfront commitments."},
    {"role": "assistant", "content": "AWS pay-as-you-go with on-demand instances fits that perfectly."},
]

_DEMO_DOCUMENTS = [
    {
        "id": "aws_compliance",
        "content": (
            "Please note that AWS holds the following compliance certifications: "
            "PCI-DSS Level 1, SOC 2 Type II, ISO 27001, HIPAA eligible. "
            "GDPR data processing agreements are available. "
            "EU data centres: eu-west-1 (Ireland) and eu-central-1 (Frankfurt)."
        ),
    },
    {
        "id": "aws_pricing",
        "content": (
            "AWS pricing model: pay-as-you-go with no upfront commitment required. "
            "Reserved instances offer up to 72% savings for steady-state workloads."
        ),
    },
    # Near-duplicate of aws_compliance — should be caught by deduplicator
    {
        "id": "aws_compliance_copy",
        "content": (
            "It is important to note that AWS compliance certifications include "
            "PCI-DSS Level 1, SOC 2 Type II, ISO 27001, and HIPAA. "
            "GDPR agreements are available for EU customers. "
            "As mentioned above, EU regions include Ireland and Frankfurt."
        ),
    },
    # Exact duplicate — caught by exact hash dedup
    {
        "id": "aws_pricing_dup",
        "content": (
            "AWS pricing model: pay-as-you-go with no upfront commitment required. "
            "Reserved instances offer up to 72% savings for steady-state workloads."
        ),
    },
    # Irrelevant — should be pruned by context_pruner
    {
        "id": "office_lunch_menu",
        "content": "Today's cafeteria menu: pasta, salad bar, grilled chicken, vegetarian options available.",
    },
    {
        "id": "hr_benefits",
        "content": "HR update: dental plan now covers orthodontics. Vision reimbursement increased to $300/year.",
    },
    {
        "id": "parking_policy",
        "content": "Parking permits must be renewed annually. Please submit your vehicle registration to facilities.",
    },
]

_DEMO_TOOLS = [
    {"name": "get_compliance_report", "description": "Fetch the latest compliance certification report for a cloud provider.", "input_schema": {"provider": "string"}},
    {"name": "compare_cloud_pricing", "description": "Compare infrastructure pricing between two cloud providers.", "input_schema": {"provider_a": "string", "provider_b": "string"}},
    {"name": "send_email",            "description": "Send an email to a recipient.", "input_schema": {"to": "string", "body": "string"}},
    {"name": "order_office_supplies", "description": "Order supplies from the office stationery catalogue.", "input_schema": {"items": "array"}},
    {"name": "book_conference_room",  "description": "Book a conference room for a meeting.", "input_schema": {"room": "string", "time": "string"}},
]


@router.get("/optimize/demo", response_model=OptimizeResponse)
async def optimize_demo():
    """
    Zero-argument demo endpoint. Runs the optimizer on a realistic
    mixed-noise payload and returns token reduction stats.

    The payload is designed to exercise all 5 optimizer steps:
      - history_compressor : 12-turn conversation compressed to summary + 6
      - deduplicator       : 1 exact duplicate + 1 near-duplicate document removed
      - context_pruner     : 3 irrelevant documents removed (cafeteria, HR, parking)
      - tool_selector      : 3 irrelevant tools removed (email, supplies, room booking)
      - prompt_compressor  : filler phrases stripped from compliance document

    No request body needed. Open in browser or hit with:
        curl http://localhost:8000/api/v1/optimize/demo
    """
    return _run_optimize(
        question=_DEMO_QUESTION,
        conversation=_DEMO_CONVERSATION,
        documents=_DEMO_DOCUMENTS,
        tools=_DEMO_TOOLS,
    )
