"""
embedder.py

Responsible for converting text into numerical vectors (embeddings).

Why this is its own module:
    - The embedding model is the most likely component to swap out later.
      Right now we use a local sentence-transformers model.
      Later this becomes an AWS Bedrock Titan Embeddings API call.
    - Isolating it here means pruner.py and scorer.py never need to change
      when we upgrade the model.

Current backend:
    - sentence-transformers: all-MiniLM-L6-v2
      * Fast, runs entirely locally — no API key needed
      * 384-dimensional output vectors
      * Good quality for a prototype

Future backend (AWS):
    - amazon.titan-embed-text-v1 via boto3 + AWS Bedrock
      * Drop-in replacement: same input/output contract
      * Swap happens only inside this file
"""

from typing import List
import numpy as np

_model = None
_MODEL_NAME = "all-MiniLM-L6-v2"


def get_embedder():
    """
    Return the singleton embedding model, loading it on first call.

    Lazy loading avoids slow startup when the module is imported
    but embed() hasn't been called yet.
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

        print(f"[embedder] Loading model '{_MODEL_NAME}'...")
        _model = SentenceTransformer(_MODEL_NAME)
        print(f"[embedder] Model loaded.")

    return _model


def embed(texts: List[str]) -> np.ndarray:
    """
    Convert a list of text strings into a 2D array of embedding vectors.

    Args:
        texts: List of strings to embed.

    Returns:
        np.ndarray of shape (len(texts), embedding_dim).
    """
    if not texts:
        return np.array([])

    model = get_embedder()
    vectors = model.encode(texts, convert_to_numpy=True)
    return vectors


def embed_query(query: str) -> np.ndarray:
    """
    Convenience wrapper to embed a single query string.

    Args:
        query: The user's question or search string.

    Returns:
        np.ndarray of shape (embedding_dim,) — a 1D vector.
    """
    vectors = embed([query])
    return vectors[0]
