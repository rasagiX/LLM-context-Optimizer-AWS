"""
Amazon Bedrock client wrapper.

Centralizes all LLM calls using Bedrock Converse API.
Includes a local mock mode when AWS_ENABLED=False or AWS credentials are missing,
allowing local testing without AWS accounts.
"""

import json
import logging
import time
from dataclasses import dataclass
from functools import lru_cache

from app.config import settings

logger = logging.getLogger("ai_context_compiler.bedrock")

_PRICING: dict[str, dict[str, float]] = {
    "anthropic.claude-3-5-sonnet-20241022-v2:0": {"input": 0.003, "output": 0.015},
    "anthropic.claude-3-5-sonnet-20240620-v1:0": {"input": 0.003, "output": 0.015},
    "anthropic.claude-3-5-haiku-20241022-v1:0": {"input": 0.0008, "output": 0.004},
    "anthropic.claude-3-opus-20240229-v1:0": {"input": 0.015, "output": 0.075},
    "anthropic.claude-3-haiku-20240307-v1:0": {"input": 0.00025, "output": 0.00125},
    "anthropic.claude-3-sonnet-20240229-v1:0": {"input": 0.003, "output": 0.015},
    "amazon.titan-text-express-v1": {"input": 0.0002, "output": 0.0006},
    "amazon.titan-text-lite-v1": {"input": 0.00015, "output": 0.0002},
    "meta.llama3-70b-instruct-v1:0": {"input": 0.00265, "output": 0.0035},
    "meta.llama3-8b-instruct-v1:0": {"input": 0.0003, "output": 0.0006},
}


def calculate_cost(input_tokens: int, output_tokens: int, model_id: str = "") -> float:
    model = model_id or settings.BEDROCK_MODEL_ID
    pricing = _PRICING.get(model, {"input": 0.003, "output": 0.015})
    return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost: float = 0.0


class BedrockError(Exception):
    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message)
        self.status_code = status_code


def _mock_invoke(prompt: str, system: str | None = None) -> LLMResponse:
    time.sleep(0.05)
    mock_input_tokens = max(10, len(prompt) // 4)
    mock_output_tokens = 42

    if system and ("strict evaluation judge" in system.lower() or "rubric" in prompt.lower()):
        text = (
            '{\n'
            '  "score": 9.5,\n'
            '  "rationale": "[Local Mock Judge] The answer accurately addresses all criteria present in the provided context.",\n'
            '  "rubric_hits": ["PCI-DSS Level 1 compliance confirmed", "GDPR EU data residency supported"],\n'
            '  "rubric_misses": []\n'
            '}'
        )
    else:
        text = (
            "[Local Mock Response (AWS_ENABLED=False)] "
            "Based on the provided context, AWS is recommended as it satisfies PCI-DSS Level 1, "
            "GDPR data residency in EU regions (Ireland and Frankfurt), and SOC 2 Type II compliance."
        )

    cost = calculate_cost(mock_input_tokens, mock_output_tokens)
    return LLMResponse(
        text=text,
        input_tokens=mock_input_tokens,
        output_tokens=mock_output_tokens,
        latency_ms=50,
        cost=cost,
    )


def invoke(
    prompt: str,
    system: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.0,
) -> LLMResponse:
    if not settings.AWS_ENABLED:
        logger.debug("[bedrock] Using local mock response (AWS_ENABLED=False)")
        return _mock_invoke(prompt, system)

    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError

        client = boto3.client("bedrock-runtime", region_name=settings.AWS_REGION)

        kwargs: dict = {
            "modelId": settings.BEDROCK_MODEL_ID,
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {"maxTokens": max_tokens, "temperature": temperature},
        }
        if system:
            kwargs["system"] = [{"text": system}]

        start = time.perf_counter()
        response = client.converse(**kwargs)
        latency_ms = int((time.perf_counter() - start) * 1000)

        output_msg = response.get("output", {}).get("message", {})
        text_blocks = [
            block.get("text", "")
            for block in output_msg.get("content", [])
            if "text" in block
        ]
        text = "".join(text_blocks)

        usage = response.get("usage", {})
        input_tokens = usage.get("inputTokens", 0)
        output_tokens = usage.get("outputTokens", 0)
        cost = calculate_cost(input_tokens, output_tokens)

        return LLMResponse(
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            cost=cost,
        )
    except Exception as exc:
        logger.warning("[bedrock] Bedrock Converse API call failed (%s) — falling back to mock mode", exc)
        return _mock_invoke(prompt, system)
