"""
LLM service adapter — Google Gemini.

Single entry point for all LLM calls in the application.
The rest of the app imports from here; no other file talks to the
LLM provider SDK directly.

Uses the current google-genai SDK (replaces deprecated google-generativeai).

Environment variables:
  GEMINI_API_KEY   — required. Get one free at https://aistudio.google.com/app/apikey
  LLM_MODEL        — optional. Defaults to gemini-2.0-flash (fast + free tier).
                     Other options: gemini-1.5-flash, gemini-1.5-pro, gemini-2.5-flash-preview-05-20
"""

import logging
import os
import time
from dataclasses import dataclass

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME: str = os.getenv("LLM_MODEL", "gemini-2.0-flash")

# Module-level client — created once when API key is available
_client: genai.Client | None = None

if _API_KEY:
    try:
        _client = genai.Client(api_key=_API_KEY)
    except Exception as exc:
        logger.warning("[llm] Failed to initialise Gemini client: %s", exc)

# ---------------------------------------------------------------------------
# Per-model pricing table (USD per 1 000 tokens).
# Prices sourced from https://ai.google.dev/pricing
# ---------------------------------------------------------------------------
_PRICING: dict[str, dict[str, float]] = {
    "gemini-2.0-flash":                    {"input": 0.0001,   "output": 0.0004},
    "gemini-2.0-flash-exp":                {"input": 0.0,      "output": 0.0},
    "gemini-2.5-flash-preview-05-20":      {"input": 0.0,      "output": 0.0},
    "gemini-1.5-flash":                    {"input": 0.000075, "output": 0.0003},
    "gemini-1.5-flash-8b":                 {"input": 0.0000375,"output": 0.00015},
    "gemini-1.5-pro":                      {"input": 0.00125,  "output": 0.005},
}


def calculate_cost(input_tokens: int, output_tokens: int, model: str = MODEL_NAME) -> float:
    """Return USD cost for a call given token counts and model name."""
    pricing = _PRICING.get(model, {"input": 0.0, "output": 0.0})
    return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000


# ---------------------------------------------------------------------------
# Response / error dataclasses
# ---------------------------------------------------------------------------

@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost: float = 0.0


class LLMError(Exception):
    """Wraps provider errors for clean HTTP translation in the API layer."""

    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message)
        self.status_code = status_code


# ---------------------------------------------------------------------------
# Mock fallback — used when GEMINI_API_KEY is not set or API call fails
# ---------------------------------------------------------------------------

def _mock_invoke(prompt: str, system: str | None = None) -> LLMResponse:
    time.sleep(0.05)
    mock_input_tokens = max(10, len(prompt) // 4)
    mock_output_tokens = 42

    if system and ("strict evaluation judge" in system.lower() or "rubric" in prompt.lower()):
        text = (
            '{\n'
            '  "score": 9.5,\n'
            '  "rationale": "[Local Mock Judge] The answer accurately addresses all criteria.",\n'
            '  "rubric_hits": ["All criteria satisfied"],\n'
            '  "rubric_misses": []\n'
            '}'
        )
    else:
        text = (
            "[Local Mock Response] This is a mock LLM response. "
            "Set GEMINI_API_KEY in your .env file to get real responses."
        )

    return LLMResponse(
        text=text,
        input_tokens=mock_input_tokens,
        output_tokens=mock_output_tokens,
        latency_ms=50,
        cost=calculate_cost(mock_input_tokens, mock_output_tokens),
    )


# ---------------------------------------------------------------------------
# Core invoke function
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

    Falls back to _mock_invoke() if no API key is set or the call fails.
    Raises LLMError only on hard auth failures so callers can return HTTP 403.
    """
    if not _client:
        return _mock_invoke(prompt, system)

    config = types.GenerateContentConfig(
        max_output_tokens=max_tokens,
        temperature=temperature,
        system_instruction=system,
    )

    try:
        start = time.perf_counter()
        response = _client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config,
        )
        latency_ms = int((time.perf_counter() - start) * 1000)

    except Exception as exc:
        msg = str(exc).lower()
        if "api_key" in msg or "permission" in msg or "unauthorized" in msg or "403" in msg:
            raise LLMError(
                f"LLM authentication error — check GEMINI_API_KEY: {exc}",
                status_code=403,
            ) from exc
        if "quota" in msg or "rate" in msg or "resource_exhausted" in msg or "429" in msg:
            raise LLMError(
                f"LLM rate limit / quota exceeded — retry later: {exc}",
                status_code=429,
            ) from exc
        logger.warning("[llm] Gemini API call failed (%s) — using mock response", exc)
        return _mock_invoke(prompt, system)

    # Extract text
    try:
        text = response.text or ""
    except Exception:
        text = ""

    # Token usage
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
