"""
Run storage.

Uses DynamoDB when the DYNAMODB_TABLE_NAME environment variable is set,
otherwise falls back to an in-memory dict (useful for local development
without AWS credentials).

DynamoDB table requirements:
  - Partition key: run_id (String)
  - No sort key needed
  - Recommended: enable TTL on an 'expires_at' attribute to auto-expire old runs

Set DYNAMODB_TABLE_NAME in your .env to enable persistence.
"""

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

_TABLE_NAME: str = os.getenv("DYNAMODB_TABLE_NAME", "")

# In-memory fallback store — used when DYNAMODB_TABLE_NAME is not set.
_RUNS: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# DynamoDB helpers
# ---------------------------------------------------------------------------

def _get_table():
    """Return a boto3 DynamoDB Table resource (created fresh per call — low
    volume operation so no caching needed; boto3 resource is lightweight)."""
    import boto3  # noqa: PLC0415
    region = os.getenv("AWS_REGION", "us-east-1")
    dynamodb = boto3.resource("dynamodb", region_name=region)
    return dynamodb.Table(_TABLE_NAME)


def _to_dynamo(run_id: str, data: dict) -> dict:
    """Serialise the run data for DynamoDB storage."""
    return {
        "run_id": run_id,
        # Store the full payload as a JSON string to avoid DynamoDB type
        # restrictions on nested floats and None values.
        "payload": json.dumps(data, default=str),
    }


def _from_dynamo(item: dict) -> dict:
    """Deserialise a DynamoDB item back to the original run dict."""
    return json.loads(item["payload"])


# ---------------------------------------------------------------------------
# Public interface — identical whether DynamoDB or in-memory is active
# ---------------------------------------------------------------------------

def save_run(run_id: str, data: dict) -> None:
    """Persist a run result. Logs a warning and falls back to memory on error."""
    if not _TABLE_NAME:
        _RUNS[run_id] = data
        return

    try:
        _get_table().put_item(Item=_to_dynamo(run_id, data))
    except Exception as exc:  # pragma: no cover
        logger.warning(
            "DynamoDB save_run failed for %s, falling back to memory: %s", run_id, exc
        )
        _RUNS[run_id] = data


def get_run(run_id: str) -> Optional[dict]:
    """Retrieve a run result by ID. Returns None if not found."""
    if not _TABLE_NAME:
        return _RUNS.get(run_id)

    try:
        response = _get_table().get_item(Key={"run_id": run_id})
        item = response.get("Item")
        if item is None:
            # Not in DynamoDB — check memory fallback (handles saves that
            # failed to DynamoDB and were kept in memory).
            return _RUNS.get(run_id)
        return _from_dynamo(item)
    except Exception as exc:  # pragma: no cover
        logger.warning(
            "DynamoDB get_run failed for %s, checking memory fallback: %s", run_id, exc
        )
        return _RUNS.get(run_id)


def list_runs(limit: int = 50) -> list[dict]:
    """
    Return up to `limit` run summaries (run_id only).
    DynamoDB scan is used — not recommended for large tables.
    In-memory mode returns all stored run IDs.
    """
    if not _TABLE_NAME:
        return [{"run_id": k} for k in list(_RUNS.keys())[-limit:]]

    try:
        response = _get_table().scan(
            ProjectionExpression="run_id",
            Limit=limit,
        )
        return response.get("Items", [])
    except Exception as exc:  # pragma: no cover
        logger.warning("DynamoDB list_runs failed: %s", exc)
        return [{"run_id": k} for k in list(_RUNS.keys())[-limit:]]
