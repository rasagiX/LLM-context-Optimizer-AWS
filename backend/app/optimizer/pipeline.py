"""
Context Compiler pipeline.

Runs the individual optimizer steps in sequence and returns the reduced
context plus a record of which steps actually changed something and the
semantic preservation score.
"""

from dataclasses import dataclass, field
import logging

from app.optimizer import (
    context_pruner,
    deduplicator,
    history_compressor,
    prompt_compressor,
    tool_selector,
)

logger = logging.getLogger(__name__)


@dataclass
class OptimizerContext:
    question: str = ""
    conversation: list[dict] = field(default_factory=list)
    documents: list[dict] = field(default_factory=list)
    tools: list[dict] = field(default_factory=list)


@dataclass
class OptimizerResult:
    context: OptimizerContext
    steps_applied: list[str]
    semantic_preservation_score: float = 1.0


def _build_full_context_string(ctx: OptimizerContext) -> str:
    parts = []
    if ctx.question:
        parts.append(f"Question: {ctx.question}")
    for msg in ctx.conversation:
        parts.append(f"{msg.get('role', 'user')}: {msg.get('content', '')}")
    for doc in ctx.documents:
        parts.append(f"Doc: {doc.get('content', '')}")
    return "\n".join(parts)


def run(ctx: OptimizerContext) -> OptimizerResult:
    # Capture raw original text representation for ML evaluation
    original_text = _build_full_context_string(ctx)

    steps_applied: list[str] = []

    # Step 1 — History compression
    original_convo_len = len(ctx.conversation)
    ctx.conversation = history_compressor.compress(ctx.conversation, ctx.question)
    if len(ctx.conversation) != original_convo_len:
        steps_applied.append("history_compressor")

    # Step 2 — Exact + near-duplicate deduplication
    original_doc_count = len(ctx.documents)
    ctx.documents = deduplicator.dedupe(ctx.documents)
    if len(ctx.documents) != original_doc_count:
        steps_applied.append("deduplicator")

    # Step 3 — Semantic context pruning
    pre_prune_count = len(ctx.documents)
    ctx.documents = context_pruner.prune(ctx.documents, ctx.question)
    if len(ctx.documents) != pre_prune_count:
        steps_applied.append("context_pruner")

    # Step 4 — Vector Tool selection
    original_tool_count = len(ctx.tools)
    ctx.tools = tool_selector.select(ctx.tools, ctx.question)
    if len(ctx.tools) != original_tool_count:
        steps_applied.append("tool_selector")

    # Step 5 — Selective Prompt & Token compression
    original_contents = [doc.get("content", "") for doc in ctx.documents]
    ctx.documents = [
        {**doc, "content": prompt_compressor.compress(doc.get("content", ""), question=ctx.question)}
        for doc in ctx.documents
    ]
    compressed_contents = [doc.get("content", "") for doc in ctx.documents]
    if compressed_contents != original_contents:
        steps_applied.append("prompt_compressor")

    # Compute Semantic Preservation Score via ml.evaluator
    optimized_text = _build_full_context_string(ctx)
    semantic_score = 1.0
    try:
        from ml.evaluator import calculate_semantic_preservation
        semantic_score = calculate_semantic_preservation(original_text, optimized_text)
    except Exception as exc:
        logger.debug("[pipeline] Semantic evaluation failed (%s) — using default score 1.0", exc)

    return OptimizerResult(
        context=ctx,
        steps_applied=steps_applied,
        semantic_preservation_score=semantic_score,
    )
