"""
Amazon Bedrock client wrapper.

Centralizes all LLM calls so the rest of the app never talks to boto3
directly. Swap MODEL_ID or the client setup here if you move providers.
"""

import json
import os
import time
from dataclasses import dataclass
from functools import lru_cache

import boto3
from botocore.exceptions import BotoCoreError, ClientError

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# ---------------------------------------------------------------------------
# Per-model pricing table (USD per 1 000 tokens).
# Add entries here as new models are supported; falls back to 0.0 if unknown.
# Prices sourced from AWS Bedrock pricing page (on-demand, us-east-1).
# ---------------------------------------------------------------------------
_PRICING: dict[str, dict[str, float]] = {
    # Claude 3.5 Sonnet v2
    "anthropic.claude-3-5-sonnet-20241022-v2:0": {"input": 0.003, "output": 0.015},
    # Claude 3.5 Sonnet v1
    "anthropic.claude-3-5-sonnet-20240620-v1:0": {"input": 0.003, "output": 0.015},
    # Claude 3.5 Haiku
    "anthropic.claude-3-5-haiku-20241022-v1:0": {"input": 0.0008, "output": 0.004},
    # Claude 3 Opus
    "anthropic.claude-3-opus-20240229-v1:0": {"input": 0.015, "output": 0.075},
    # Claude 3 Haiku
    "anthropic.claude-3-haiku-20240307-v1:0": {"input": 0.00025, "output": 0.00125},
    # Claude 3 Sonnet
    "anthropic.claude-3-sonnet-20240229-v1:0": {"input": 0.003, "output": 0.015},
    # Amazon Titan Text Express
    "amazon.titan-text-express-v1": {"input": 0.0002, "output": 0.0006},
    # Amazon Titan Text Lite
    "amazon.titan-text-lite-v1": {"input": 0.00015, "output": 0.0002},
    # Meta Llama 3 70B Instruct
    "meta.llama3-70b-instruct-v1:0": {"input": 0.00265, "output": 0.0035},
    # Meta Llama 3 8B Instruct
    "meta.llama3-8b-instruct-v1:0": {"input": 0.0003, "output": 0.0006},
}


def calculate_cost(input_tokens: int, output_tokens: int, model_id: str = MODEL_ID) -> float:
    """Return USD cost for a call given token counts and model ID."""
    pricing = _PRICING.get(model_id, {"input": 0.0, "output": 0.0})
    return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost: float = 0.0


@lru_cache(maxsize=1)
def _get_client():
    """Return a cached boto3 bedrock-runtime client (singleton per process)."""
    return boto3.client("bedrock-runtime", region_name=AWS_REGION)


class BedrockError(Exception):
    """Wraps boto3 ClientError / BotoCoreError for clean HTTP translation."""

    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message)
        self.status_code = status_code


def invoke(
    prompt: str,
    system: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.0,
) -> LLMResponse:
    """
    Send a single-turn prompt to the configured Bedrock model and return
    the answer plus token/latency/cost metrics.

    Raises BedrockError (with an HTTP-friendly status_code) on failure so
    callers can translate directly to HTTPException without importing boto3.
    """
    body: dict = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system

    try:
        start = time.perf_counter()
        response = _get_client().invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(body),
        )
        latency_ms = int((time.perf_counter() - start) * 1000)
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in ("AccessDeniedException", "UnauthorizedException"):
            raise BedrockError(
                f"Bedrock access denied — check IAM permissions and that model "
                f"'{MODEL_ID}' is enabled in region '{AWS_REGION}': {exc}",
                status_code=403,
            ) from exc
        if error_code == "ValidationException":
            raise BedrockError(f"Bedrock validation error: {exc}", status_code=400) from exc
        if error_code == "ThrottlingException":
            raise BedrockError(f"Bedrock throttled — retry later: {exc}", status_code=429) from exc
        raise BedrockError(f"Bedrock call failed ({error_code}): {exc}", status_code=503) from exc
    except BotoCoreError as exc:
        raise BedrockError(f"AWS connectivity error: {exc}", status_code=503) from exc

    payload = json.loads(response["body"].read())
    text = "".join(
        block.get("text", "")
        for block in payload.get("content", [])
        if block.get("type") == "text"
    )
    usage = payload.get("usage", {})
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)

    return LLMResponse(
        text=text,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        cost=calculate_cost(input_tokens, output_tokens),
    )
