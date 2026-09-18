"""
Context Compiler pipeline.

Runs the individual optimizer steps in sequence and returns the reduced
context plus a record of which steps actually changed something.

steps_applied only lists a step if it measurably changed the context:
    - history_compressor : listed if conversation length decreased
    - deduplicator       : listed if document count decreased
    - context_pruner     : listed if document count decreased
    - tool_selector      : listed if tool count decreased
    - prompt_compressor  : listed if any document content was shortened
"""

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

    # Step 4 — Tool selection
    original_tool_count = len(ctx.tools)
    ctx.tools = tool_selector.select(ctx.tools, ctx.question)
    if len(ctx.tools) != original_tool_count:
        steps_applied.append("tool_selector")

    # Step 5 — Prompt compression (whitespace + filler phrase removal)
    original_contents = [doc.get("content", "") for doc in ctx.documents]
    ctx.documents = [
        {**doc, "content": prompt_compressor.compress(doc["content"])}
        for doc in ctx.documents
    ]
    compressed_contents = [doc.get("content", "") for doc in ctx.documents]
    if compressed_contents != original_contents:
        steps_applied.append("prompt_compressor")

    return OptimizerResult(context=ctx, steps_applied=steps_applied)
