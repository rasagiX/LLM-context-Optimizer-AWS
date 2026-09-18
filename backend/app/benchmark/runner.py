"""
Runs the fixed benchmark suite (app/benchmark/tasks.json) through the
same run() logic used by POST /api/v1/run, so benchmark results and
ad-hoc run results are always produced the same way.

The task set must not change after optimization work begins (see project
spec) — this file only reads tasks.json, it never writes to it.
"""

import json
from pathlib import Path

from app.api.runs import run as run_endpoint
from app.schemas.requests import DocumentInput, Message, RunRequest, ToolDefinition

TASKS_PATH = Path(__file__).parent / "tasks.json"


def load_tasks(task_ids: list[str] | None = None) -> list[dict]:
    with open(TASKS_PATH) as f:
        tasks = json.load(f)
    if task_ids:
        tasks = [t for t in tasks if t["id"] in task_ids]
    return tasks


async def run_benchmark(task_ids: list[str] | None = None) -> list[dict]:
    tasks = load_tasks(task_ids)
    results = []

    for task in tasks:
        req = RunRequest(
            task_id=task["id"],
            question=task["question"],
            conversation=[Message(**m) for m in task.get("conversation", [])],
            documents=[DocumentInput(**d) for d in task.get("documents", [])],
            tools=[ToolDefinition(**t) for t in task.get("tools", [])],
            rubric=task.get("rubric", []),
            mode="compare",
        )
        response = await run_endpoint(req)
        result = response.model_dump()
        result["task_id"] = task["id"]
        result["category"] = task.get("category")
        results.append(result)

    return results
