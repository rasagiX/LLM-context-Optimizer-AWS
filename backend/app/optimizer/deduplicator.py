"""
Deduplicator.

Baseline implementation: exact-match dedup by normalized content hash.

TODO: near-duplicate detection (e.g. same paragraph reworded across two
retrieved chunks) needs fuzzy matching or embeddings — exact-match is
the cheap v0 to unblock the rest of the pipeline.
"""

import hashlib


def _fingerprint(text: str) -> str:
    normalized = " ".join(text.split()).lower()
    return hashlib.sha256(normalized.encode()).hexdigest()


def dedupe(documents: list[dict]) -> list[dict]:
    seen: set[str] = set()
    result = []
    for doc in documents:
        fp = _fingerprint(doc.get("content", ""))
        if fp in seen:
            continue
        seen.add(fp)
        result.append(doc)
    return result
