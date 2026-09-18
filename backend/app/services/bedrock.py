"""
Amazon Bedrock client wrapper.

Centralizes all LLM calls so the rest of the app never talks to boto3
directly. Swap MODEL_ID or the client setup here if you move providers.
"""

import json
import os
import time
from dataclasses import dataclass

import boto3

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: int


def _client():
    return boto3.client("bedrock-runtime", region_name=AWS_REGION)


def invoke(
    prompt: str,
    system: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.0,
) -> LLMResponse:
    """
    Send a single-turn prompt to the configured Bedrock model and return
    the answer plus token/latency metrics.

    Raises whatever boto3/ClientError raises on failure — callers should
    handle that (e.g. api/runs.py) and translate to an HTTP error.
    """
    body: dict = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system

    start = time.perf_counter()
    response = _client().invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body),
    )
    latency_ms = int((time.perf_counter() - start) * 1000)

    payload = json.loads(response["body"].read())
    text = "".join(
        block.get("text", "") for block in payload.get("content", []) if block.get("type") == "text"
    )
    usage = payload.get("usage", {})

    return LLMResponse(
        text=text,
        input_tokens=usage.get("input_tokens", 0),
        output_tokens=usage.get("output_tokens", 0),
        latency_ms=latency_ms,
    )
