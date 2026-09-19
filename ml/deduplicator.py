"""
deduplicator.py

Embedding-based near-duplicate detection for context chunks.

Why exact hashing isn't enough:
    Two chunks can say essentially the same thing with different wording:
        "Ibuprofen causes stomach bleeding with long-term use."
        "Long-term ibuprofen consumption leads to gastrointestinal bleeding."
    A SHA-256 hash treats these as completely different. Cosine similarity
    on their embeddings will score them ~0.92 — clearly duplicates.

How this works:
    1. Embed all chunks in one batch
    2. Build a pairwise similarity matrix (vectorized, fast)
    3. Greedily keep each chunk only if it isn't too similar to any
       already-kept chunk (similarity below `threshold`)

Threshold guidance:
    0.95+ → only near-verbatim duplicates removed (conservative)
    0.85  → paraphrases and rewordings removed (recommended default)
    0.70  → aggressive — removes topically similar but distinct chunks
"""

from typing import List
import numpy as np


def deduplicate_by_embedding(
    texts: List[str],
    threshold: float = 0.85,
) -> List[int]:
    """
    Return the indices of chunks to keep after near-duplicate removal.

    Uses greedy deduplication: iterate chunks in order, keep a chunk only
    if its cosine similarity to every already-kept chunk is below `threshold`.
    The first occurrence of a near-duplicate group is always kept.

    Args:
        texts:     List of text strings to deduplicate.
        threshold: Cosine similarity above which two chunks are considered
                   near-duplicates. The second occurrence is dropped.

    Returns:
        List of integer indices (into `texts`) to keep, in original order.

    Example:
        >>> texts = ["The sky is blue.", "The sky appears blue.", "Grass is green."]
        >>> keep = deduplicate_by_embedding(texts, threshold=0.85)
        >>> keep  # [0, 2] — index 1 is a near-duplicate of index 0
        [0, 2]
    """
    if not texts:
        return []

    if len(texts) == 1:
        return [0]

    # Import here so the module can be imported without sentence-transformers
    # installed (the embedder raises a clean ImportError on first call).
    from ml.embedder import embed

    vectors = embed(texts)  # shape: (n, d)

    # Row-normalise for fast cosine similarity via dot product
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1e-10, norms)
    unit_vectors = vectors / norms  # shape: (n, d)

    kept_indices: List[int] = []
    kept_units: List[np.ndarray] = []

    for i, unit_vec in enumerate(unit_vectors):
        if not kept_units:
            kept_indices.append(i)
            kept_units.append(unit_vec)
            continue

        # Compute similarity against all already-kept chunks at once
        kept_matrix = np.stack(kept_units)          # shape: (k, d)
        sims = kept_matrix @ unit_vec               # shape: (k,)
        max_sim = float(sims.max())

        if max_sim < threshold:
            kept_indices.append(i)
            kept_units.append(unit_vec)
        # else: near-duplicate of an already-kept chunk — skip it

    return kept_indices


def deduplicate_texts(
    texts: List[str],
    threshold: float = 0.85,
) -> List[str]:
    """
    Convenience wrapper: return the deduplicated list of strings directly.

    Args:
        texts:     List of text strings.
        threshold: Near-duplicate similarity threshold.

    Returns:
        Filtered list of strings with near-duplicates removed.
    """
    keep = deduplicate_by_embedding(texts, threshold=threshold)
    return [texts[i] for i in keep]
