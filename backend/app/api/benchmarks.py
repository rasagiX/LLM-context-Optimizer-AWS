"""POST /api/v1/benchmarks/run — run the fixed benchmark suite."""

from fastapi import APIRouter

from app.benchmark import metrics, runner
from app.schemas.requests import BenchmarkRunRequest

router = APIRouter()


@router.post("/benchmarks/run")
async def run_benchmark(req: BenchmarkRunRequest):
    results = await runner.run_benchmark(req.task_ids)
    summary = metrics.summarize(results)
    return {"results": results, "summary": summary}
