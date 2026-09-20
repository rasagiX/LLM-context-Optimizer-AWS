"""
Run storage service.

Supports both DynamoDB and S3 persistence with in-memory fallback.
"""

import json
import logging
import os
from typing import Optional

from app.services import s3

logger = logging.getLogger(__name__)

_TABLE_NAME: str = os.getenv("DYNAMODB_TABLE_NAME", "")
_RUNS: dict[str, dict] = {}


def _get_table():
    import boto3  # noqa: PLC0415
    region = os.getenv("AWS_REGION", "us-east-1")
    dynamodb = boto3.resource("dynamodb", region_name=region)
    return dynamodb.Table(_TABLE_NAME)


def _to_dynamo(run_id: str, data: dict) -> dict:
    return {
        "run_id": run_id,
        "payload": json.dumps(data, default=str),
    }


def _from_dynamo(item: dict) -> dict:
    return json.loads(item["payload"])


def save_run(run_id: str, data: dict) -> None:
    """Persist a run result to memory, S3, and DynamoDB (if enabled)."""
    _RUNS[run_id] = data

    # Attempt S3 save
    s3.save_json(f"runs/{run_id}.json", data)

    # Attempt DynamoDB save if configured
    if _TABLE_NAME:
        try:
            _get_table().put_item(Item=_to_dynamo(run_id, data))
        except Exception as exc:
            logger.warning("DynamoDB save_run failed for %s: %s", run_id, exc)


def get_run(run_id: str) -> Optional[dict]:
    """Retrieve a run result by ID."""
    if run_id in _RUNS:
        return _RUNS[run_id]

    if _TABLE_NAME:
        try:
            response = _get_table().get_item(Key={"run_id": run_id})
            item = response.get("Item")
            if item:
                data = _from_dynamo(item)
                _RUNS[run_id] = data
                return data
        except Exception as exc:
            logger.warning("DynamoDB get_run failed for %s: %s", run_id, exc)

    # Attempt load from S3 fallback
    remote_data = s3.load_json(f"runs/{run_id}.json")
    if remote_data:
        _RUNS[run_id] = remote_data
        return remote_data

    return None


def list_runs(limit: int = 50) -> list[dict]:
    """Return up to `limit` run summaries (run_id only)."""
    if not _TABLE_NAME:
        return [{"run_id": k} for k in list(_RUNS.keys())[-limit:]]

    try:
        response = _get_table().scan(
            ProjectionExpression="run_id",
            Limit=limit,
        )
        return response.get("Items", [])
    except Exception as exc:
        logger.warning("DynamoDB list_runs failed: %s", exc)
        return [{"run_id": k} for k in list(_RUNS.keys())[-limit:]]
