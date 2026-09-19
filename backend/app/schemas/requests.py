"""Request schemas for the API layer."""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)


class DocumentInput(BaseModel):
    id: str
    content: str


class RunRequest(BaseModel):
    """POST /api/v1/run — run a task through baseline and/or optimized pipeline."""

    task_id: Optional[str] = None
    question: Optional[str] = None
    conversation: list[Message] = Field(default_factory=list)
    documents: list[DocumentInput] = Field(default_factory=list)
    tools: list[ToolDefinition] = Field(default_factory=list)
    rubric: list[str] = Field(default_factory=list)
    mode: Literal["baseline", "optimized", "compare"] = "compare"


class OptimizeRequest(BaseModel):
    """POST /api/v1/optimize — optimize a context without calling the LLM."""

    question: Optional[str] = None
    conversation: list[Message] = Field(default_factory=list)
    documents: list[DocumentInput] = Field(default_factory=list)
    tools: list[ToolDefinition] = Field(default_factory=list)


class EvaluateRequest(BaseModel):
    """POST /api/v1/evaluate — score an answer against a rubric."""

    question: str
    answer: str
    rubric: list[str] = Field(default_factory=list)


class BenchmarkRunRequest(BaseModel):
    """POST /api/v1/benchmarks/run — run the fixed benchmark suite."""

    task_ids: Optional[list[str]] = None  # None = run all tasks in tasks.json
