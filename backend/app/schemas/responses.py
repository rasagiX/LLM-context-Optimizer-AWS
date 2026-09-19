"""Response schemas for the API layer."""

from typing import Optional

from pydantic import BaseModel, Field


class PipelineResult(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int
    cost: float
    answer: str


class QualityScore(BaseModel):
    score: float
    rationale: Optional[str] = None
    rubric_hits: list[str] = Field(default_factory=list)
    rubric_misses: list[str] = Field(default_factory=list)


class ComparisonSummary(BaseModel):
    token_reduction_percent: Optional[float] = None
    cost_reduction_percent: Optional[float] = None
    latency_reduction_percent: Optional[float] = None
    quality_baseline: Optional[float] = None
    quality_optimized: Optional[float] = None


class RunResponse(BaseModel):
    run_id: str
    baseline: Optional[PipelineResult] = None
    optimized: Optional[PipelineResult] = None
    comparison: Optional[ComparisonSummary] = None


class OptimizeResponse(BaseModel):
    optimized_context: dict
    original_tokens: int
    optimized_tokens: int
    reduction_percent: float
    steps_applied: list[str] = Field(default_factory=list)
    tokens_saved: Optional[int] = None
    optimization_latency_ms: Optional[int] = None
    cost_saved_est: Optional[float] = None


class EvaluateResponse(BaseModel):
    quality: QualityScore

