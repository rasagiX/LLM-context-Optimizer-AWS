"""
Centralized Application Configuration.

Loads environment variables with sensible defaults.
Supports AWS_ENABLED flag for local mock mode when AWS credentials are not available.
"""

import os
from dataclasses import dataclass


def _str_to_bool(val: str | None, default: bool = False) -> bool:
    if val is None or val.strip() == "":
        return default
    return val.strip().lower() in ("true", "1", "yes", "on")


@dataclass
class Settings:
    # ── LLM Provider ─────────────────────────────────────────────────────────
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")

    # ── AWS (optional — only needed for DynamoDB, S3, CloudWatch) ────────────
    AWS_ENABLED: bool = _str_to_bool(os.getenv("AWS_ENABLED", "false"), default=False)
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")

    # ── Embedder ─────────────────────────────────────────────────────────────
    # "local" uses sentence-transformers (default, no API key needed)
    # "bedrock" uses Amazon Titan Embeddings V2 (requires AWS credentials)
    EMBEDDER_BACKEND: str = os.getenv("EMBEDDER_BACKEND", "local").lower()

    # ── Storage ───────────────────────────────────────────────────────────────
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "ai-context-compiler-artifacts")
    DYNAMODB_TABLE_NAME: str = os.getenv("DYNAMODB_TABLE_NAME", "")
    CLOUDWATCH_LOG_GROUP: str = os.getenv("CLOUDWATCH_LOG_GROUP", "/aws/fastapi/ai-context-compiler")

    # ── Optimizer tuning ─────────────────────────────────────────────────────
    MAX_CONTEXT_TOKENS: int = int(os.getenv("MAX_CONTEXT_TOKENS", "128000"))
    RELEVANCE_THRESHOLD: float = float(os.getenv("RELEVANCE_THRESHOLD", "0.2"))
    OPTIMIZATION_ENABLED: bool = _str_to_bool(os.getenv("OPTIMIZATION_ENABLED", "true"), default=True)


settings = Settings()
