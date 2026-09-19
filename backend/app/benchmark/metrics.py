"""Aggregate metrics across a set of benchmark run results."""

from statistics import mean


def summarize(results: list[dict]) -> dict:
    """
    results: list of dicts shaped like RunResponse.model_dump(), each with
    baseline/optimized/comparison populated (mode="compare" assumed).
    """
    token_reductions = [
        r["comparison"]["token_reduction_percent"]
        for r in results
        if r.get("comparison") and r["comparison"].get("token_reduction_percent") is not None
    ]
    quality_baseline = [
        r["comparison"]["quality_baseline"]
        for r in results
        if r.get("comparison") and r["comparison"].get("quality_baseline") is not None
    ]
    quality_optimized = [
        r["comparison"]["quality_optimized"]
        for r in results
        if r.get("comparison") and r["comparison"].get("quality_optimized") is not None
    ]

    return {
        "tasks_run": len(results),
        "avg_token_reduction_percent": round(mean(token_reductions), 2) if token_reductions else None,
        "avg_quality_baseline": round(mean(quality_baseline), 2) if quality_baseline else None,
        "avg_quality_optimized": round(mean(quality_optimized), 2) if quality_optimized else None,
    }
