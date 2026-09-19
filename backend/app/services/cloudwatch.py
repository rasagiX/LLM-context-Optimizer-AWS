"""
CloudWatch integration service.

Emits custom metrics (TokensSaved, OptimizationLatency, TokenReductionPercent, PipelineCalls)
and logs pipeline events to AWS CloudWatch when AWS_ENABLED=True.
Falls back gracefully to local logging when AWS is disabled or credentials are missing.
"""

import logging
from typing import Any

from app.config import settings

logger = logging.getLogger("ai_context_compiler.cloudwatch")

_cw_client = None


def _get_cloudwatch_client():
    global _cw_client
    if not settings.AWS_ENABLED:
        return None
    if _cw_client is None:
        try:
            import boto3

            _cw_client = boto3.client("cloudwatch", region_name=settings.AWS_REGION)
        except Exception as exc:
            logger.warning("[cloudwatch] Failed to initialize CloudWatch client: %s", exc)
            _cw_client = None
    return _cw_client


def put_metric(metric_name: str, value: float, unit: str = "Count", dimensions: list[dict[str, str]] | None = None) -> None:
    """
    Put a custom metric data point into AWS CloudWatch CloudWatch Metrics namespace 'AIContextCompiler'.
    """
    client = _get_cloudwatch_client()
    if client is None:
        logger.debug("[cloudwatch local] Metric %s: %s (%s)", metric_name, value, unit)
        return

    try:
        metric_data: dict[str, Any] = {
            "MetricName": metric_name,
            "Value": float(value),
            "Unit": unit,
        }
        if dimensions:
            metric_data["Dimensions"] = dimensions

        client.put_metric_data(
            Namespace="AIContextCompiler",
            MetricData=[metric_data],
        )
        logger.debug("[cloudwatch] Emitted metric %s = %s", metric_name, value)
    except Exception as exc:
        logger.error("[cloudwatch] Error emitting metric %s: %s", metric_name, exc)


def log_pipeline_execution(
    endpoint: str,
    original_tokens: int,
    optimized_tokens: int,
    reduction_percent: float,
    latency_ms: int,
) -> None:
    """
    Helper to log and record metrics for an optimizer pipeline execution.
    """
    tokens_saved = max(0, original_tokens - optimized_tokens)
    logger.info(
        "[%s] original_tokens=%d optimized_tokens=%d tokens_saved=%d reduction=%.2f%% latency=%dms",
        endpoint,
        original_tokens,
        optimized_tokens,
        tokens_saved,
        reduction_percent,
        latency_ms,
    )

    put_metric("TokensSaved", float(tokens_saved), unit="Count", dimensions=[{"Name": "Endpoint", "Value": endpoint}])
    put_metric("OptimizationLatency", float(latency_ms), unit="Milliseconds", dimensions=[{"Name": "Endpoint", "Value": endpoint}])
    put_metric("TokenReductionPercent", float(reduction_percent), unit="Percent", dimensions=[{"Name": "Endpoint", "Value": endpoint}])
    put_metric("PipelineCalls", 1.0, unit="Count", dimensions=[{"Name": "Endpoint", "Value": endpoint}])
