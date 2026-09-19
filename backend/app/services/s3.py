"""
AWS S3 storage service.

Saves run results, benchmark reports, and evaluations to Amazon S3.
Falls back seamlessly when AWS is disabled or S3 bucket is unavailable.
"""

import json
import logging
from typing import Any, Optional

from app.config import settings

logger = logging.getLogger("ai_context_compiler.s3")

_s3_client = None


def _get_s3_client():
    global _s3_client
    if not settings.AWS_ENABLED:
        return None
    if _s3_client is None:
        try:
            import boto3

            _s3_client = boto3.client("s3", region_name=settings.AWS_REGION)
        except Exception as exc:
            logger.warning("[s3] Failed to initialize S3 client: %s", exc)
            _s3_client = None
    return _s3_client


def save_json(key: str, data: dict[str, Any]) -> bool:
    """
    Save a dictionary as a JSON object to S3.
    """
    client = _get_s3_client()
    if client is None:
        logger.debug("[s3 local] Skipped saving key %s (S3 disabled)", key)
        return False

    try:
        content = json.dumps(data, indent=2)
        client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key,
            Body=content.encode("utf-8"),
            ContentType="application/json",
        )
        logger.info("[s3] Saved s3://%s/%s", settings.S3_BUCKET_NAME, key)
        return True
    except Exception as exc:
        logger.error("[s3] Error writing %s to S3: %s", key, exc)
        return False


def load_json(key: str) -> Optional[dict[str, Any]]:
    """
    Load a JSON object from S3.
    """
    client = _get_s3_client()
    if client is None:
        return None

    try:
        response = client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
        body = response["Body"].read().decode("utf-8")
        return json.loads(body)
    except Exception as exc:
        logger.warning("[s3] Could not read %s from S3: %s", key, exc)
        return None
