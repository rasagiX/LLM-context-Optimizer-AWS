"""
embedder.py

Responsible for converting text into numerical vectors (embeddings).

Why this is its own module:
    - The embedding model is the most likely component to swap out later.
      Right now we use a local sentence-transformers model.
      Later this becomes an AWS Bedrock Titan Embeddings API call.
    - Isolating it here means pruner.py, scorer.py, and deduplicator.py
      never need to change when we upgrade the model.

Current backend:
    - sentence-transformers: all-MiniLM-L6-v2
      * Fast, runs entirely locally — no API key needed
      * 384-dimensional output vectors
      * Good quality for a prototype

Future backend (AWS):
    - amazon.titan-embed-text-v1 via boto3 + AWS Bedrock
      * Drop-in replacement: same input/output contract
      * Swap happens only inside this file

Async safety:
    model.encode() is a blocking CPU call. In an async FastAPI app, calling
    it directly on the event loop starves other requests for its duration.
    embed_async() and embed_query_async() run the blocking call in a thread
    pool executor so the event loop stays free.
"""

import asyncio
import logging
from typing import List

import numpy as np

logger = logging.getLogger(__name__)

_model = None
_MODEL_NAME = "all-MiniLM-L6-v2"


def get_embedder():
    """
    Return the singleton embedding model, loading it on first call.

    Lazy loading avoids slow startup when the module is imported
    but embed() hasn't been called yet (e.g. during tests that mock
    this function, or when running the backend without ml deps installed).
    """
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Run: pip install sentence-transformers"
            ) from e

        logger.info("[embedder] Loading model '%s'...", _MODEL_NAME)
        _model = SentenceTransformer(_MODEL_NAME)
        logger.info("[embedder] Model loaded.")

    return _model


# ---------------------------------------------------------------------------
# Synchronous API (use in scripts, tests, and non-async contexts)
# ---------------------------------------------------------------------------

def embed(texts: List[str]) -> np.ndarray:
    """
    Convert a list of text strings into a 2D array of embedding vectors.

    BLOCKING — do not call directly from an async FastAPI route or service.
    Use embed_async() instead.

    Args:
        texts: List of strings to embed.

    Returns:
        np.ndarray of shape (len(texts), embedding_dim).

    Example:
        >>> vecs = embed(["Hello world", "How are you?"])
        >>> vecs.shape
        (2, 384)
    """
    if not texts:
        return np.array([])

    model = get_embedder()
    vectors = model.encode(texts, convert_to_numpy=True)
    return vectors


def embed_query(query: str) -> np.ndarray:
    """
    Convenience wrapper: embed a single query string synchronously.

    BLOCKING — use embed_query_async() from async contexts.

    Args:
        query: The user's question or search string.

    Returns:
        np.ndarray of shape (embedding_dim,) — a 1D vector.
    """
    return embed([query])[0]


# ---------------------------------------------------------------------------
# Async API (use from FastAPI route handlers and async services)
# ---------------------------------------------------------------------------

async def embed_async(texts: List[str]) -> np.ndarray:
    """
    Non-blocking version of embed(). Runs model.encode() in a thread pool
    executor so the asyncio event loop is not blocked during inference.

    Args:
        texts: List of strings to embed.

    Returns:
        np.ndarray of shape (len(texts), embedding_dim).

    Example (inside a FastAPI route or async service):
        vectors = await embed_async(["chunk one", "chunk two"])
    """
    if not texts:
        return np.array([])

    loop = asyncio.get_event_loop()
    # run_in_executor offloads the blocking call to the default ThreadPoolExecutor
    vectors = await loop.run_in_executor(None, embed, texts)
    return vectors


async def embed_query_async(query: str) -> np.ndarray:
    """
    Non-blocking version of embed_query(). Use from async FastAPI handlers.

    Args:
        query: The user's question or search string.

    Returns:
        np.ndarray of shape (embedding_dim,) — a 1D vector.
    """
    vectors = await embed_async([query])
    return vectors[0]
