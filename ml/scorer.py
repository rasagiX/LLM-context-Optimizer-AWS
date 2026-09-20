"""
scorer.py

Responsible for computing relevance scores between a query and context chunks.

This module is intentionally kept pure:
    - No model loading
    - No I/O
    - Only math on numpy arrays

This makes it fast, easy to test, and easy to swap scoring methods later.
"""

from typing import List, Tuple
import numpy as np


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Compute cosine similarity between two 1D vectors.

    Args:
        vec_a: First vector, shape (d,).
        vec_b: Second vector, shape (d,).

    Returns:
        Float in [-1, 1]. Higher means more similar.
    """
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        raise ValueError(
            "Cannot compute cosine similarity with a zero-magnitude vector. "
            "This usually means an empty string was embedded."
        )

    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


def score_chunks(
    query_vector: np.ndarray,
    chunk_vectors: np.ndarray,
) -> np.ndarray:
    """
    Compute cosine similarity between one query vector and many chunk vectors.

    Uses vectorized numpy operations — much faster than a Python loop.

    Args:
        query_vector:  1D array of shape (d,).
        chunk_vectors: 2D array of shape (n_chunks, d).

    Returns:
        1D array of shape (n_chunks,) with a similarity score per chunk.
    """
    query_norm = np.linalg.norm(query_vector)
    if query_norm == 0:
        raise ValueError("Query vector has zero magnitude — was an empty string embedded?")
    query_unit = query_vector / query_norm

    chunk_norms = np.linalg.norm(chunk_vectors, axis=1, keepdims=True)
    chunk_norms = np.where(chunk_norms == 0, 1e-10, chunk_norms)
    chunk_units = chunk_vectors / chunk_norms

    scores = chunk_units @ query_unit
    return scores


def rank_chunks(
    chunks: List[str],
    scores: np.ndarray,
    top_k: int = 5,
    threshold: float = 0.0,
) -> List[Tuple[str, float]]:
    """
    Sort chunks by score and apply top_k / threshold filtering.

    Args:
        chunks:    Original list of text chunks.
        scores:    Similarity score for each chunk, same length as chunks.
        top_k:     Maximum number of chunks to return. -1 = no limit.
        threshold: Minimum score a chunk must have to be included.

    Returns:
        List of (chunk_text, score) tuples, sorted by score descending.
    """
    if len(chunks) != len(scores):
        raise ValueError(
            f"chunks length ({len(chunks)}) must match scores length ({len(scores)})"
        )

    paired = sorted(zip(chunks, scores.tolist()), key=lambda x: x[1], reverse=True)

    if threshold > 0.0:
        paired = [(chunk, score) for chunk, score in paired if score >= threshold]

    if top_k > 0:
        paired = paired[:top_k]

    return paired
