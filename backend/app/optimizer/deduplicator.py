"""
Deduplicator.

Two-stage deduplication:
    Stage 1 — Exact dedup: SHA-256 hash on normalised content.
              Fast, zero-cost, catches copy-paste duplicates.

    Stage 2 — Near-duplicate dedup: cosine similarity on sentence embeddings (via ml package)
              with Jaccard shingle fallback.
"""

import hashlib
import logging
import re

logger = logging.getLogger(__name__)

NEAR_DUPE_THRESHOLD = 0.85
SHINGLE_SIZE = 3


def _fingerprint(text: str) -> str:
    normalized = " ".join(text.split()).lower()
    return hashlib.sha256(normalized.encode()).hexdigest()


def _shingles(text: str, k: int = SHINGLE_SIZE) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    if len(words) < k:
        return {" ".join(words)}
    return {" ".join(words[i : i + k]) for i in range(len(words) - k + 1)}


def _jaccard(set_a: set, set_b: set) -> float:
    if not set_a and not set_b:
        return 1.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


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


def _jaccard_dedupe(documents: list[dict], threshold: float = NEAR_DUPE_THRESHOLD) -> list[dict]:
    kept_shingles: list[set[str]] = []
    result: list[dict] = []
    for doc in documents:
        content = doc.get("content", "")
        doc_shingles = _shingles(content)
        if any(_jaccard(doc_shingles, existing) >= threshold for existing in kept_shingles):
            continue
        kept_shingles.append(doc_shingles)
        result.append(doc)
    return result


def dedupe(
    documents: list[dict],
    similarity_threshold: float = NEAR_DUPE_THRESHOLD,
) -> list[dict]:
    """
    Remove exact and near-duplicate documents.
    """
    if not documents:
        return documents

    after_exact = _exact_dedupe(documents)

    if len(after_exact) <= 1:
        return after_exact

    try:
        from ml.deduplicator import deduplicate_by_embedding
        contents = [doc.get("content", "") for doc in after_exact]
        keep_indices = deduplicate_by_embedding(contents, threshold=similarity_threshold)
        return [after_exact[i] for i in keep_indices]
    except Exception as exc:
        logger.debug("[deduplicator] embedding dedup unavailable (%s) — using Jaccard shingles", exc)
        return _jaccard_dedupe(after_exact, threshold=similarity_threshold)
