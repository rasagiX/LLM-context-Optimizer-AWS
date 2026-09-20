"""
Context Compiler pipeline.

Runs individual optimizer steps in sequence and returns the reduced
context plus a record of applied steps and the semantic preservation score.
"""

import copy
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
    ctx = copy.deepcopy(ctx)
    original_text = _build_full_context_string(ctx)
    steps_applied: list[str] = []

    # Step 1 — History compression
    original_convo = ctx.conversation
    ctx.conversation = history_compressor.compress(ctx.conversation, ctx.question)
    if ctx.conversation != original_convo:
        steps_applied.append("history_compressor")

    # Step 2 — Deduplication
    original_docs = ctx.documents
    ctx.documents = deduplicator.dedupe(ctx.documents)
    if ctx.documents != original_docs:
        steps_applied.append("deduplicator")

    # Step 3 — Context pruning
    pruned_docs = context_pruner.prune(ctx.documents, ctx.question)
    if pruned_docs != ctx.documents:
        steps_applied.append("context_pruner")
    ctx.documents = pruned_docs

    # Step 4 — Vector Tool selection
    original_tools = ctx.tools
    ctx.tools = tool_selector.select(ctx.tools, ctx.question)
    if ctx.tools != original_tools:
        steps_applied.append("tool_selector")

    # Step 5 — Selective Prompt & Mutual Information Token compression
    compressed_docs = [
        {**doc, "content": prompt_compressor.compress(doc.get("content", ""), question=ctx.question)}
        for doc in ctx.documents
    ]
    if compressed_docs != ctx.documents:
        steps_applied.append("prompt_compressor")
    ctx.documents = compressed_docs

    # Step 6 — Tool Schema Minification
    if ctx.tools:
        try:
            from ml.schema_minifier import minify_tool_to_ts
            minified_tools = []
            for t in ctx.tools:
                if isinstance(t, dict):
                    minified_tools.append({"name": t.get("name"), "signature": minify_tool_to_ts(t)})
                else:
                    minified_tools.append(t)
            ctx.tools = minified_tools
            if "schema_minifier" not in steps_applied:
                steps_applied.append("schema_minifier")
        except Exception as exc:
            logger.debug("[pipeline] Schema minification skipped: %s", exc)

    # Compute Semantic Preservation Score
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
