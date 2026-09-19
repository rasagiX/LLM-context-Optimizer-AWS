"""
Run storage.

In-memory dict for local development. Swap this module's contents for
a DynamoDB-backed implementation in Step 10 (AWS deployment) — callers
only use get_run/save_run so the storage backend can change without
touching the API layer.
"""

from typing import Optional

_RUNS: dict[str, dict] = {}


def save_run(run_id: str, data: dict) -> None:
    _RUNS[run_id] = data


def get_run(run_id: str) -> Optional[dict]:
    return _RUNS.get(run_id)
