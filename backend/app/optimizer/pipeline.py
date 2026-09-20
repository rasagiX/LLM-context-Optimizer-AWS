"""
Context Compiler pipeline.

Runs the individual optimizer steps in sequence and returns the reduced
context plus a record of which steps changed anything, so /api/v1/optimize
and the run pipeline can report token savings per step.
"""

import copy
from dataclasses import dataclass, field

from app.optimizer import (
    context_pruner,
    deduplicator,
    history_compressor,
    prompt_compressor,
    tool_selector,
)


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


def run(ctx: OptimizerContext) -> OptimizerResult:
    """
    Run all optimizer steps against a deep copy of ctx so the caller's
    original context is never mutated.

    steps_applied records only steps that actually changed something,
    giving a consistent and accurate audit trail.
    """
    # Deep-copy so the caller retains the original unmodified context.
    ctx = copy.deepcopy(ctx)

    steps_applied: list[str] = []

    # --- Step 1: History compression ---
    original_convo = ctx.conversation
    ctx.conversation = history_compressor.compress(ctx.conversation, ctx.question)
    if ctx.conversation != original_convo:
        steps_applied.append("history_compressor")

    # --- Step 2: Deduplication ---
    original_docs = ctx.documents
    ctx.documents = deduplicator.dedupe(ctx.documents)
    if ctx.documents != original_docs:
        steps_applied.append("deduplicator")

    # --- Step 3: Context pruning ---
    pruned_docs = context_pruner.prune(ctx.documents, ctx.question)
    if pruned_docs != ctx.documents:
        steps_applied.append("context_pruner")
    ctx.documents = pruned_docs

    # --- Step 4: Tool selection ---
    original_tools = ctx.tools
    ctx.tools = tool_selector.select(ctx.tools, ctx.question)
    if ctx.tools != original_tools:
        steps_applied.append("tool_selector")

    # --- Step 5: Prompt compression ---
    compressed_docs = [
        {**doc, "content": prompt_compressor.compress(doc["content"])}
        for doc in ctx.documents
    ]
    if compressed_docs != ctx.documents:
        steps_applied.append("prompt_compressor")
    ctx.documents = compressed_docs

    return OptimizerResult(context=ctx, steps_applied=steps_applied)
