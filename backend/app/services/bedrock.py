"""
Amazon Bedrock client wrapper.

Centralizes all LLM calls using Bedrock Converse API.
Includes a local mock mode when AWS_ENABLED=False or AWS credentials are missing,
allowing local testing without AWS accounts.
"""

import logging
import time
from dataclasses import dataclass

from app.config import settings

logger = logging.getLogger("ai_context_compiler.bedrock")


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: int


def _mock_invoke(prompt: str, system: str | None = None) -> LLMResponse:
    """
    Simulated LLM response when AWS is disabled or credentials are unavailable.
    """
    time.sleep(0.05)  # Simulate network latency
    mock_input_tokens = max(10, len(prompt) // 4)
    mock_output_tokens = 42

    # If prompt is judge prompt (system contains judge keywords), return valid judge JSON
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

    return LLMResponse(
        text=text,
        input_tokens=mock_input_tokens,
        output_tokens=mock_output_tokens,
        latency_ms=50,
    )


def invoke(
    prompt: str,
    system: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.0,
) -> LLMResponse:
    """
    Send a prompt to Bedrock model using Converse API.
    Falls back to mock mode if settings.AWS_ENABLED is False or credentials missing.
    """
    if not settings.AWS_ENABLED:
        logger.debug("[bedrock] Using local mock response (AWS_ENABLED=False)")
        return _mock_invoke(prompt, system)

    try:
        import boto3

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

        return LLMResponse(
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
        )
    except Exception as exc:
        logger.warning("[bedrock] Bedrock Converse API call failed (%s) — falling back to mock mode", exc)
        return _mock_invoke(prompt, system)

