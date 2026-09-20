"""
reranker.py

Two-Stage Retrieval & Reranking Module.

Why two-stage reranking?
    Bi-encoders (like MiniLM / Titan V2) embed query and documents independently.
    They are extremely fast for filtering thousands of documents, but can miss
    subtle semantic interactions between query terms and context terms.

    Cross-encoders score (query, document) pairs jointly with full cross-attention.
    They provide higher precision ranking.

Pipeline:
    Stage 1: Bi-encoder cosine similarity filtering (fast candidate retrieval).
    Stage 2: Cross-encoder reranking (fine-grained scoring of top candidates).

If sentence-transformers cross-encoder dependencies are missing, the reranker
gracefully degrades to Stage 1 bi-encoder scores.
"""

import logging
from typing import List, Tuple
import numpy as np

from ml.embedder import embed, embed_query
from ml.scorer import score_chunks

logger = logging.getLogger(__name__)

_cross_encoder_model = None
_CROSS_ENCODER_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_CROSS_ENCODER_FAILED = False


def _get_cross_encoder():
    """Lazy loader for cross-encoder model."""
    global _cross_encoder_model, _CROSS_ENCODER_FAILED
    if _cross_encoder_model is not None:
        return _cross_encoder_model
    if _CROSS_ENCODER_FAILED:
        return None

    try:
        from sentence_transformers import CrossEncoder
        logger.info("[reranker] Loading cross-encoder '%s'...", _CROSS_ENCODER_NAME)
        _cross_encoder_model = CrossEncoder(_CROSS_ENCODER_NAME)
        logger.info("[reranker] Cross-encoder loaded.")
        return _cross_encoder_model
    except Exception as exc:
        logger.warning("[reranker] Cross-encoder unavailable (%s) — using bi-encoder scores.", exc)
        _CROSS_ENCODER_FAILED = True
        return None


def rerank_chunks(
    query: str,
    chunks: List[str],
    top_k: int = 5,
    threshold: float = 0.0,
    candidate_k: int = 15,
) -> List[Tuple[str, float]]:
    """
    Rerank text chunks against a query using a two-stage pipeline.

    Args:
        query:        User query string.
        chunks:       List of context chunk strings.
        top_k:        Final number of top chunks to return. -1 = no cap.
        threshold:    Minimum score threshold to retain a chunk.
        candidate_k:  Number of candidates to pass from Stage 1 to Stage 2.

    Returns:
        List of (chunk_text, rerank_score) tuples sorted descending.
    """
    if not query.strip() or not chunks:
        return []

    # Stage 1: Fast Bi-Encoder Filtering
    q_vec = embed_query(query)
    c_vecs = embed(chunks)
    stage1_scores = score_chunks(q_vec, c_vecs)

    # Pick top candidate_k for Stage 2 reranking
    paired_stage1 = sorted(enumerate(stage1_scores.tolist()), key=lambda x: x[1], reverse=True)
    candidates_idx = [idx for idx, _ in paired_stage1[:candidate_k]]
    candidate_chunks = [chunks[idx] for idx in candidates_idx]

    # Stage 2: Cross-Encoder Reranking
    cross_encoder = _get_cross_encoder()
    if cross_encoder is not None and candidate_chunks:
        try:
            pairs = [[query, chunk] for chunk in candidate_chunks]
            raw_scores = cross_encoder.predict(pairs)
            # Sigmoid normalization if scores are logits
            rerank_scores = (1.0 / (1.0 + np.exp(-np.array(raw_scores)))).tolist()

            reranked_pairs = list(zip(candidate_chunks, rerank_scores))
            reranked_pairs.sort(key=lambda x: x[1], reverse=True)

            # Apply threshold & top_k
            if threshold > 0.0:
                reranked_pairs = [(c, s) for c, s in reranked_pairs if s >= threshold]

            if top_k > 0:
                reranked_pairs = reranked_pairs[:top_k]

            return reranked_pairs
        except Exception as exc:
            logger.error("[reranker] Stage 2 failed: %s — falling back to Stage 1.", exc)

    # Fallback to Stage 1 Bi-Encoder scores if Stage 2 fails or is uninstalled
    fallback_pairs = [(chunks[idx], score) for idx, score in paired_stage1]
    if threshold > 0.0:
        fallback_pairs = [(c, s) for c, s in fallback_pairs if s >= threshold]

    if top_k > 0:
        fallback_pairs = fallback_pairs[:top_k]

    return fallback_pairs
