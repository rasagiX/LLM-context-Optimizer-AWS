"""
embedder.py

Responsible for converting text into numerical vectors (embeddings).

Why this is its own module:
    - The embedding model is the most likely component to swap out later.
    - Everything else (scorer, pruner, deduplicator) only sees numpy arrays
      and never needs to change when the backend switches.

Backends (controlled by EMBEDDER_BACKEND env var):
    local  (default) — sentence-transformers all-MiniLM-L6-v2, runs on CPU,
                        no API key needed, 384-dimensional vectors.
    bedrock          — AWS Bedrock Titan Embeddings V2, 1024-dimensional
                        vectors, requires AWS credentials in environment.

Switching backends:
    Set EMBEDDER_BACKEND=bedrock in backend/.env (or export it).
    Everything else in the codebase stays the same.

Async safety:
    Both backends expose embed_async() / embed_query_async() that run the
    blocking call in a thread pool executor so the FastAPI event loop is
    never blocked.
"""

import asyncio
import json
import logging
import os
from typing import List

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Backend selection
# ---------------------------------------------------------------------------

EMBEDDER_BACKEND = os.getenv("EMBEDDER_BACKEND", "local").lower()
# local   → sentence-transformers (default, works offline)
# bedrock → AWS Bedrock Titan Embeddings V2

# ---------------------------------------------------------------------------
# Local backend — sentence-transformers
# ---------------------------------------------------------------------------

_local_model = None
_LOCAL_MODEL_NAME = "all-MiniLM-L6-v2"


def _get_local_model():
    """Lazy-load the local sentence-transformers model (singleton)."""
    global _local_model
    if _local_model is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Run: pip install sentence-transformers"
            ) from e
        logger.info("[embedder] Loading local model '%s'...", _LOCAL_MODEL_NAME)
        _local_model = SentenceTransformer(_LOCAL_MODEL_NAME)
        logger.info("[embedder] Local model loaded.")
    return _local_model


def _embed_local(texts: List[str]) -> np.ndarray:
    model = _get_local_model()
    return model.encode(texts, convert_to_numpy=True)


# ---------------------------------------------------------------------------
# Bedrock backend — Amazon Titan Embeddings V2
# ---------------------------------------------------------------------------

_BEDROCK_MODEL_ID = "amazon.titan-embed-text-v2:0"
_BEDROCK_REGION   = os.getenv("AWS_REGION", "us-east-1")

# Titan Embeddings V2 supports 256, 512, or 1024 dimensions.
# 512 is the best balance of quality vs speed for our use case.
_TITAN_DIMENSIONS = 512


def _embed_bedrock(texts: List[str]) -> np.ndarray:
    """
    Embed a list of texts using Amazon Titan Embeddings V2 via Bedrock in parallel.
    Falls back to local sentence-transformers if Bedrock API fails or model access is denied.
    """
    try:
        import boto3
        from concurrent.futures import ThreadPoolExecutor

        client = boto3.client("bedrock-runtime", region_name=_BEDROCK_REGION)

        def _embed_single(text: str) -> List[float]:
            body = json.dumps({
                "inputText": text,
                "dimensions": _TITAN_DIMENSIONS,
                "normalize": True,
            })
            response = client.invoke_model(
                modelId=_BEDROCK_MODEL_ID,
                body=body,
                contentType="application/json",
                accept="application/json",
            )
            payload = json.loads(response["body"].read())
            return payload["embedding"]

        max_workers = min(10, max(1, len(texts)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            vectors = list(executor.map(_embed_single, texts))

        return np.array(vectors, dtype=np.float32)
    except Exception as exc:
        logger.warning("[embedder] Bedrock embedding call failed (%s) — falling back to local sentence-transformers", exc)
        return _embed_local(texts)


# ---------------------------------------------------------------------------
# Unified synchronous API
# ---------------------------------------------------------------------------

def embed(texts: List[str]) -> np.ndarray:
    """
    Convert a list of text strings into a 2D array of embedding vectors.

    Backend is selected by EMBEDDER_BACKEND env var:
        EMBEDDER_BACKEND=local   → all-MiniLM-L6-v2 (default)
        EMBEDDER_BACKEND=bedrock → Amazon Titan Embeddings V2

    BLOCKING — do not call from an async FastAPI handler.
    Use embed_async() instead.

    Args:
        texts: List of strings to embed.

    Returns:
        np.ndarray of shape (len(texts), embedding_dim).
        Dim is 384 for local, 512 for bedrock.
    """
    if not texts:
        return np.array([])

    if EMBEDDER_BACKEND == "bedrock":
        logger.debug("[embedder] using Bedrock Titan backend")
        return _embed_bedrock(texts)
    else:
        logger.debug("[embedder] using local sentence-transformers backend")
        return _embed_local(texts)


def embed_query(query: str) -> np.ndarray:
    """
    Embed a single query string synchronously.

    BLOCKING — use embed_query_async() from async contexts.

    Returns:
        np.ndarray of shape (embedding_dim,) — a 1D vector.
    """
    return embed([query])[0]


# ---------------------------------------------------------------------------
# Unified async API (use from FastAPI route handlers)
# ---------------------------------------------------------------------------

async def embed_async(texts: List[str]) -> np.ndarray:
    """
    Non-blocking version of embed(). Runs in a thread pool executor so
    the asyncio event loop is not blocked during model inference or API calls.

    Args:
        texts: List of strings to embed.

    Returns:
        np.ndarray of shape (len(texts), embedding_dim).
    """
    if not texts:
        return np.array([])

    loop = asyncio.get_event_loop()
    vectors = await loop.run_in_executor(None, embed, texts)
    return vectors


async def embed_query_async(query: str) -> np.ndarray:
    """
    Non-blocking version of embed_query(). Use from async FastAPI handlers.

    Returns:
        np.ndarray of shape (embedding_dim,) — a 1D vector.
    """
    vectors = await embed_async([query])
    return vectors[0]
