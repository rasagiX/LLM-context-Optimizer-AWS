"""
Context Compiler pipeline.

Runs the individual optimizer steps in sequence and returns the reduced
context plus a record of which steps changed anything, so /api/v1/optimize
and the run pipeline can report token savings per step.
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

    ctx.conversation = history_compressor.compress(ctx.conversation, ctx.question)
    if ctx.conversation:
        steps_applied.append("history_compressor")

    ctx.documents = deduplicator.dedupe(ctx.documents)
    steps_applied.append("deduplicator")

    ctx.documents = context_pruner.prune(ctx.documents, ctx.question)
    steps_applied.append("context_pruner")

    ctx.tools = tool_selector.select(ctx.tools, ctx.question)
    if ctx.tools:
        steps_applied.append("tool_selector")

    ctx.documents = [
        {**doc, "content": prompt_compressor.compress(doc["content"])} for doc in ctx.documents
    ]
    steps_applied.append("prompt_compressor")

    return OptimizerResult(context=ctx, steps_applied=steps_applied)
