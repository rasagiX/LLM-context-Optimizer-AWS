"""
Deduplicator.

Two-pass deduplication:
  1. Exact-match: SHA-256 of normalised content (fast, zero false positives).
  2. Near-duplicate: Jaccard similarity on word-level shingles (trigrams).
     Documents with Jaccard >= NEAR_DUPE_THRESHOLD are considered duplicates
     and the later occurrence is dropped.

Near-duplicate detection catches reworded or lightly edited versions of the
same chunk that exact hashing misses — common when the same source document
is retrieved multiple times with minor formatting differences.
"""

import hashlib
import re

# Jaccard similarity threshold above which two documents are treated as
# near-duplicates. 0.85 is intentionally conservative — lower values risk
# dropping legitimately distinct documents that share boilerplate.
NEAR_DUPE_THRESHOLD = 0.85

# Shingle size (number of consecutive words per shingle).
SHINGLE_SIZE = 3


def _fingerprint(text: str) -> str:
    """SHA-256 of normalised text for exact-match dedup."""
    normalized = " ".join(text.split()).lower()
    return hashlib.sha256(normalized.encode()).hexdigest()


def _shingles(text: str, k: int = SHINGLE_SIZE) -> set[str]:
    """Return the set of k-word shingles from text."""
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    if len(words) < k:
        # Document too short to shingle — use the whole word list as one unit.
        return {" ".join(words)}
    return {" ".join(words[i : i + k]) for i in range(len(words) - k + 1)}


def _jaccard(set_a: set, set_b: set) -> float:
    """Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 1.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def dedupe(documents: list[dict]) -> list[dict]:
    """
    Return documents with exact and near-duplicates removed.
    The first occurrence of each document is always kept.
    """
    if not documents:
        return documents

    seen_hashes: set[str] = set()
    kept_shingles: list[set[str]] = []
    result: list[dict] = []

    for doc in documents:
        content = doc.get("content", "")

        # --- Pass 1: exact match ---
        fp = _fingerprint(content)
        if fp in seen_hashes:
            continue
        seen_hashes.add(fp)

        # --- Pass 2: near-duplicate check ---
        doc_shingles = _shingles(content)
        is_near_dupe = any(
            _jaccard(doc_shingles, existing) >= NEAR_DUPE_THRESHOLD
            for existing in kept_shingles
        )
        if is_near_dupe:
            continue

        kept_shingles.append(doc_shingles)
        result.append(doc)

    return result
