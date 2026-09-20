"""
LLM service adapter — Google Gemini.

Single entry point for all LLM calls in the application.
The rest of the app imports from here; no other file talks to the
LLM provider SDK directly.

To swap providers in future, only this file needs to change.

Environment variables:
  GEMINI_API_KEY   — required. Get one free at https://aistudio.google.com/app/apikey
  LLM_MODEL        — optional. Defaults to gemini-1.5-flash (fast + free tier).
                     Other options: gemini-1.5-pro, gemini-2.0-flash-exp
"""

import os
import time
from dataclasses import dataclass

import google.generativeai as genai

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")

if not _API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is not set. "
        "Get a free key at https://aistudio.google.com/app/apikey and add it to your .env file."
    )

genai.configure(api_key=_API_KEY)

# ---------------------------------------------------------------------------
# Per-model pricing table (USD per 1 000 tokens).
# Gemini free tier has no cost; paid tier rates listed for reference.
# Prices sourced from https://ai.google.dev/pricing
# ---------------------------------------------------------------------------
_PRICING: dict[str, dict[str, float]] = {
    # Gemini 1.5 Flash — free tier up to 15 RPM / 1M TPM
    "gemini-1.5-flash":         {"input": 0.000075, "output": 0.0003},
    "gemini-1.5-flash-8b":      {"input": 0.0000375, "output": 0.00015},
    # Gemini 1.5 Pro
    "gemini-1.5-pro":           {"input": 0.00125, "output": 0.005},
    # Gemini 2.0 Flash
    "gemini-2.0-flash-exp":     {"input": 0.0, "output": 0.0},  # free experimental
    "gemini-2.0-flash":         {"input": 0.0001, "output": 0.0004},
    # Gemini 2.5 Flash
    "gemini-2.5-flash-preview-05-20": {"input": 0.0, "output": 0.0},
}


def calculate_cost(input_tokens: int, output_tokens: int, model: str = MODEL_NAME) -> float:
    """Return USD cost for a call given token counts and model name."""
    pricing = _PRICING.get(model, {"input": 0.0, "output": 0.0})
    return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000


# ---------------------------------------------------------------------------
# Response dataclass — identical shape to the old LLMResponse so callers
# require zero changes.
# ---------------------------------------------------------------------------

@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost: float = 0.0


# ---------------------------------------------------------------------------
# Error class — replaces BedrockError, same interface (status_code attribute)
# ---------------------------------------------------------------------------

class LLMError(Exception):
    """Wraps provider errors for clean HTTP translation in the API layer."""

    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message)
        self.status_code = status_code


# ---------------------------------------------------------------------------
# Core invoke function — identical signature to the old bedrock.invoke()
# ---------------------------------------------------------------------------

def invoke(
    prompt: str,
    system: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.0,
) -> LLMResponse:
    """
    Send a single-turn prompt to the configured Gemini model and return
    the answer plus token/latency/cost metrics.

    Raises LLMError (with an HTTP-friendly status_code) on failure so
    callers can translate directly to HTTPException without importing the
    provider SDK.

    Args:
        prompt:      The user-facing prompt text.
        system:      Optional system instruction (maps to Gemini system_instruction).
        max_tokens:  Maximum output tokens (maps to max_output_tokens).
        temperature: Sampling temperature (0.0 = deterministic).
    """
    try:
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        model_kwargs: dict = {
            "model_name": MODEL_NAME,
            "generation_config": generation_config,
        }
        if system:
            model_kwargs["system_instruction"] = system

        model = genai.GenerativeModel(**model_kwargs)

        start = time.perf_counter()
        response = model.generate_content(prompt)
        latency_ms = int((time.perf_counter() - start) * 1000)

    except Exception as exc:
        # Map common Gemini / google-generativeai errors to HTTP status codes.
        msg = str(exc).lower()
        if "api_key" in msg or "permission" in msg or "unauthorized" in msg:
            raise LLMError(
                f"LLM authentication error — check GEMINI_API_KEY: {exc}",
                status_code=403,
            ) from exc
        if "quota" in msg or "rate" in msg or "resource_exhausted" in msg:
            raise LLMError(
                f"LLM rate limit / quota exceeded — retry later: {exc}",
                status_code=429,
            ) from exc
        if "invalid" in msg or "bad request" in msg:
            raise LLMError(f"LLM invalid request: {exc}", status_code=400) from exc
        raise LLMError(f"LLM call failed: {exc}", status_code=503) from exc

    # Extract text
    try:
        text = response.text
    except Exception:
        # response.text raises if the response was blocked by safety filters
        text = ""

    # Token usage — Gemini returns usage_metadata on the response object
    usage = getattr(response, "usage_metadata", None)
    input_tokens = getattr(usage, "prompt_token_count", 0) or 0
    output_tokens = getattr(usage, "candidates_token_count", 0) or 0

    return LLMResponse(
        text=text,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        cost=calculate_cost(input_tokens, output_tokens),
    )
