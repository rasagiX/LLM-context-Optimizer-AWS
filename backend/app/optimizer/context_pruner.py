"""
Context Pruner.

Uses semantic embedding similarity (via the ml/ package) to score each
document against the question and keep only the most relevant ones.

Replaces the original keyword-overlap baseline. The ml/ module handles
all embedding and scoring logic — this file is purely an adapter that
bridges the backend's list[dict] interface to the ml module's interface.

Adapter contract:
    Backend pipeline calls:  prune(documents, question) -> list[dict]
    ml module exposes:       prune_context(query, context_chunks) -> dict

The key interface difference:
    - Backend passes full dicts: [{"id": "doc1", "content": "..."}]
    - ml module works on plain strings: ["..."]
    - After scoring, we reconstruct full dicts by index so "id" is preserved

Fallback behaviour (no ML available):
    If sentence-transformers is not installed (e.g. during backend-only
    development without the ml deps), the module falls back to keyword
    overlap so the server still starts and /optimize still works.
"""

import logging

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------
# Attempt to import the ML module. Fall back gracefully if not installed.
# --------------------------------------------------------------------------
try:
    from ml.embedder import embed
    from ml.scorer import score_chunks, rank_chunks
    _ML_AVAILABLE = True
except ImportError:
    _ML_AVAILABLE = False
    logger.warning(
        "[context_pruner] sentence-transformers not installed — "
        "falling back to keyword overlap. "
        "Run: pip install sentence-transformers"
    )


# --------------------------------------------------------------------------
# Semantic pruning (primary path)
# --------------------------------------------------------------------------

def _prune_semantic(
    documents: list[dict],
    question: str,
    top_k: int = -1,
    threshold: float = 0.1,
) -> list[dict]:
    """
    Score documents against the question using cosine similarity on
    sentence embeddings, then keep those above the threshold.

    Args:
        documents:  List of dicts with at least a "content" key.
        question:   The user's query string.
        top_k:      Max documents to keep. -1 = no hard limit (use threshold only).
        threshold:  Minimum cosine similarity to keep a document.
                    0.1 is intentionally low — we want to discard clearly
                    unrelated documents (score ~0.0) but keep anything that
                    has even marginal relevance.

    Returns:
        Filtered list of original dicts, ordered by relevance (best first).
        Always returns at least one document to avoid sending empty context.
    """
    contents = [doc.get("content", "") for doc in documents]

    # Embed everything in one batch (efficient — single model forward pass)
    query_vector = embed([question])[0]
    chunk_vectors = embed(contents)

    scores = score_chunks(query_vector, chunk_vectors)

    # rank_chunks returns (text, score) pairs — we use the text to map back
    # to original dicts by index rather than string equality (safer for
    # documents with identical content snippets)
    score_list = scores.tolist()
    indexed = sorted(
        enumerate(score_list), key=lambda x: x[1], reverse=True
    )

    # Apply threshold filter
    kept = [(i, s) for i, s in indexed if s >= threshold]

    # Apply top_k cap
    if top_k > 0:
        kept = kept[:top_k]

    # Always keep at least the single best-scoring document
    if not kept:
        best_idx = max(range(len(score_list)), key=lambda i: score_list[i])
        kept = [(best_idx, score_list[best_idx])]

    # Reconstruct original dicts in relevance order, preserving all keys
    result = [documents[i] for i, _ in kept]

    logger.debug(
        "[context_pruner] semantic: %d -> %d documents (threshold=%.2f)",
        len(documents), len(result), threshold,
    )
    return result


# --------------------------------------------------------------------------
# Keyword-overlap fallback (used only when ml deps are missing)
# --------------------------------------------------------------------------

import re

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
    threshold: float = 0.1,
) -> list[dict]:
    """
    Remove documents that are not semantically relevant to the question.

    This is the function called by pipeline.py. It delegates to the
    semantic (ML) implementation when available, and falls back to keyword
    overlap otherwise.

    Args:
        documents:  List of dicts with "id" and "content" keys.
        question:   The user's query string.
        top_k:      Hard cap on number of documents returned. -1 = no cap.
        threshold:  Minimum cosine similarity (semantic) or keyword overlap
                    (fallback) to keep a document.

    Returns:
        Filtered list of document dicts, best matches first.
    """
    if not documents:
        return documents

    if not question or not question.strip():
        # No question to score against — return everything unchanged
        return documents

    if _ML_AVAILABLE:
        return _prune_semantic(documents, question, top_k=top_k, threshold=threshold)
    else:
        return _prune_keyword(documents, question, min_overlap=0.05)
