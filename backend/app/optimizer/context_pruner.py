"""
Context Pruner.

Uses semantic embedding similarity (via the ml/ package) to score each
document against the question and keep only the most relevant ones.

Replaces the original keyword-overlap baseline. The ml/ module handles
all embedding and scoring logic — this file is purely an adapter that
bridges the backend's list[dict] interface to the ml module's interface.

Adapter contract:
    Backend pipeline calls:  prune(documents, question) -> list[dict]
    ml module exposes:       embed() + score_chunks() from ml.embedder / ml.scorer

The key interface difference:
    - Backend passes full dicts: [{"id": "doc1", "content": "..."}]
    - ml module works on plain strings: ["..."]
    - After scoring, we reconstruct full dicts by index so "id" is preserved

Fallback behaviour (no ML available):
    If sentence-transformers is not installed (e.g. disk space issue or
    backend-only dev environment), the module falls back to keyword overlap
    so the server still starts and /optimize still works.
"""

import logging
import re

import numpy as np

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------
# Semantic pruning (primary path)
# --------------------------------------------------------------------------

def _prune_semantic(
    documents: list[dict],
    question: str,
    top_k: int = -1,
    threshold: float = 0.2,
) -> list[dict]:
    """
    Score documents against the question using cosine similarity on
    sentence embeddings, then keep those above the threshold.

    Imports ml.embedder and ml.scorer lazily so any ImportError is caught
    by the caller and triggers the keyword fallback.

    Args:
        documents:  List of dicts with at least a "content" key.
        question:   The user's query string.
        top_k:      Max documents to keep. -1 = no hard limit (threshold only).
        threshold:  Minimum cosine similarity to keep a document.
                    0.1 is intentionally low — discard clearly unrelated docs
                    but keep anything with marginal relevance.

    Returns:
        Filtered list of original dicts, ordered by relevance (best first).
        Always returns at least one document to avoid sending empty context.
    """
    # Lazy import — keeps ImportError catchable at call time
    from ml.embedder import embed
    from ml.scorer import score_chunks

    contents = [doc.get("content", "") for doc in documents]

    # Embed everything in one batch (single model forward pass)
    query_vector = embed([question])[0]
    chunk_vectors = embed(contents)

    scores = score_chunks(query_vector, chunk_vectors)
    score_list = scores.tolist()

    # Sort by score descending (index-based to preserve original dicts)
    indexed = sorted(enumerate(score_list), key=lambda x: x[1], reverse=True)

    # Apply threshold filter
    kept = [(i, s) for i, s in indexed if s >= threshold]

    # Apply top_k cap
    if top_k > 0:
        kept = kept[:top_k]

    # Always keep at least the single best-scoring document
    if not kept:
        best_idx = max(range(len(score_list)), key=lambda i: score_list[i])
        kept = [(best_idx, score_list[best_idx])]

    # Reconstruct original dicts in relevance order, all keys preserved
    result = [documents[i] for i, _ in kept]

    logger.debug(
        "[context_pruner] semantic: %d -> %d documents (threshold=%.2f)",
        len(documents), len(result), threshold,
    )
    return result


# --------------------------------------------------------------------------
# Keyword-overlap fallback (used only when ml deps are missing)
# --------------------------------------------------------------------------

_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "in", "on", "of", "to",
    "and", "or", "for", "with", "what", "how", "why", "does", "do", "did",
}


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def _prune_keyword(
    documents: list[dict],
    question: str,
    min_overlap: float = 0.05,
) -> list[dict]:
    q_keywords = _keywords(question)
    if not q_keywords:
        return documents

    scored = []
    for doc in documents:
        doc_keywords = _keywords(doc.get("content", ""))
        overlap = len(q_keywords & doc_keywords) / max(len(q_keywords), 1)
        scored.append((overlap, doc))

    kept = [doc for overlap, doc in scored if overlap >= min_overlap]
    if not kept:
        kept = [max(scored, key=lambda pair: pair[0])[1]]
    return kept


# --------------------------------------------------------------------------
# Public interface (called by pipeline.py)
# --------------------------------------------------------------------------

def prune(
    documents: list[dict],
    question: str,
    top_k: int = -1,
    threshold: float = 0.2,
) -> list[dict]:
    """
    Remove documents that are not semantically relevant to the question.

    Tries semantic (ML) pruning first. Falls back to keyword overlap if
    sentence-transformers is not installed or fails for any reason.

    Args:
        documents:  List of dicts with "id" and "content" keys.
        question:   The user's query string.
        top_k:      Hard cap on number of documents returned. -1 = no cap.
        threshold:  Minimum cosine similarity to keep a document.

    Returns:
        Filtered list of document dicts, best matches first.
    """
    if not documents:
        return documents

    if not question or not question.strip():
        return documents

    try:
        return _prune_semantic(documents, question, top_k=top_k, threshold=threshold)
    except ImportError:
        logger.warning(
            "[context_pruner] sentence-transformers not available — "
            "falling back to keyword overlap. "
            "Run: pip install sentence-transformers"
        )
        return _prune_keyword(documents, question)
    except Exception as exc:
        logger.error(
            "[context_pruner] semantic pruning failed (%s) — "
            "falling back to keyword overlap.", exc
        )
        return _prune_keyword(documents, question)
