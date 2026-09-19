"""
Run storage service.

Uses in-memory cache for fast local reads, and persists run data
to AWS S3 when AWS_ENABLED=True.
"""

from typing import Optional

from app.services import s3

_RUNS: dict[str, dict] = {}


def save_run(run_id: str, data: dict) -> None:
    _RUNS[run_id] = data
    # Attempt to persist to S3 under key "runs/{run_id}.json"
    s3.save_json(f"runs/{run_id}.json", data)


def get_run(run_id: str) -> Optional[dict]:
    if run_id in _RUNS:
        return _RUNS[run_id]

    # If not in memory, attempt load from S3
    remote_data = s3.load_json(f"runs/{run_id}.json")
    if remote_data:
        _RUNS[run_id] = remote_data
        return remote_data

    return None

