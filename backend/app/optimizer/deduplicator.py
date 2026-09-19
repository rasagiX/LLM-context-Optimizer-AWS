"""
Deduplicator.

Two-stage deduplication:
    Stage 1 — Exact dedup: SHA-256 hash on normalised content.
              Fast, zero-cost, catches copy-paste duplicates.

    Stage 2 — Near-duplicate dedup: cosine similarity on sentence embeddings.
              Catches paraphrased or reworded duplicates that exact hashing
              misses (e.g. "ibuprofen causes bleeding" vs
              "long-term ibuprofen leads to gastrointestinal bleeding").

If sentence-transformers is not installed, only Stage 1 runs and a warning
is logged — the pipeline still works, just without near-dup detection.
"""

import hashlib
import logging

logger = logging.getLogger(__name__)

try:
    from ml.deduplicator import deduplicate_by_embedding
    _ML_AVAILABLE = True
except ImportError:
    _ML_AVAILABLE = False
    logger.warning(
        "[deduplicator] sentence-transformers not installed — "
        "near-duplicate detection disabled, exact dedup only."
    )


# --------------------------------------------------------------------------
# Stage 1: exact dedup
# --------------------------------------------------------------------------

def _fingerprint(text: str) -> str:
    normalized = " ".join(text.split()).lower()
    return hashlib.sha256(normalized.encode()).hexdigest()


def _exact_dedupe(documents: list[dict]) -> list[dict]:
    seen: set[str] = set()
    result = []
    for doc in documents:
        fp = _fingerprint(doc.get("content", ""))
        if fp in seen:
            continue
        seen.add(fp)
        result.append(doc)
    return result


# --------------------------------------------------------------------------
# Public interface (called by pipeline.py)
# --------------------------------------------------------------------------

def dedupe(
    documents: list[dict],
    similarity_threshold: float = 0.85,
) -> list[dict]:
    """
    Remove exact and near-duplicate documents.

    Stage 1 (always): exact content-hash dedup.
    Stage 2 (when ml deps present): embedding cosine similarity dedup.

    Args:
        documents:            List of dicts with "id" and "content" keys.
        similarity_threshold: Cosine similarity above which two documents
                              are treated as near-duplicates. The later
                              occurrence is dropped.

    Returns:
        Deduplicated list of document dicts in original order.
    """
    if not documents:
        return documents

    # Stage 1 — exact dedup (always runs)
    after_exact = _exact_dedupe(documents)

    exact_removed = len(documents) - len(after_exact)
    if exact_removed:
        logger.debug("[deduplicator] exact: removed %d duplicate(s)", exact_removed)

    if not _ML_AVAILABLE or len(after_exact) <= 1:
        return after_exact

    # Stage 2 — near-duplicate dedup via embeddings
    contents = [doc.get("content", "") for doc in after_exact]

    try:
        keep_indices = deduplicate_by_embedding(contents, threshold=similarity_threshold)
        result = [after_exact[i] for i in keep_indices]

        near_removed = len(after_exact) - len(result)
        if near_removed:
            logger.debug(
                "[deduplicator] near-dup: removed %d near-duplicate(s) "
                "(threshold=%.2f)",
                near_removed, similarity_threshold,
            )

        return result

    except Exception as exc:
        # Never let dedup failure crash the pipeline — return exact-deduped
        # result and log the error
        logger.error("[deduplicator] near-dup stage failed: %s", exc)
        return after_exact
