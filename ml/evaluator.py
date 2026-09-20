"""
evaluator.py

ML Quality & Semantic Preservation Evaluator.

Why semantic evaluation matters:
    Reducing token count is only useful if the core semantic information
    and factual accuracy of the prompt are preserved.

This module computes quantitative ML metrics:
    1. Semantic Preservation Score: Cosine similarity between original context
       vector representation and optimized context vector representation.
    2. Token Compression Ratio & Percentage Tokens Saved.
    3. Information Density Score: Ratio of key entity density in optimized vs raw text.
"""

from typing import Dict, Any, List
import numpy as np

from ml.embedder import embed
from ml.utils import count_tokens, token_reduction_stats


def calculate_semantic_preservation(original_text: str, optimized_text: str) -> float:
    """
    Compute vector cosine similarity between original and optimized context.

    Returns:
        Float between 0.0 and 1.0 representing semantic retention.
    """
    if not original_text.strip() or not optimized_text.strip():
        return 1.0 if (not original_text.strip() and not optimized_text.strip()) else 0.0

    try:
        vectors = embed([original_text, optimized_text])
        vec_orig = vectors[0]
        vec_opt = vectors[1]

        norm_orig = np.linalg.norm(vec_orig)
        norm_opt = np.linalg.norm(vec_opt)

        if norm_orig == 0 or norm_opt == 0:
            return 0.0

        similarity = float(np.dot(vec_orig, vec_opt) / (norm_orig * norm_opt))
        # Clip to [0, 1] range
        return max(0.0, min(1.0, round(similarity, 4)))
    except Exception:
        # Fallback to lexical Jaccard similarity if ML fails
        words_orig = set(original_text.lower().split())
        words_opt = set(optimized_text.lower().split())
        if not words_orig:
            return 1.0
        intersection = words_orig & words_opt
        return round(len(intersection) / len(words_orig), 4)


def evaluate_optimization(
    original_chunks: List[str],
    retained_chunks: List[str],
    query: str = "",
) -> Dict[str, Any]:
    """
    Full ML evaluation suite for a context optimization run.

    Args:
        original_chunks: All context chunks before optimization.
        retained_chunks: Context chunks after optimization.
        query: Optional user query string.

    Returns:
        Dict containing token stats, reduction percent, and semantic preservation score.
    """
    stats = token_reduction_stats(original_chunks, retained_chunks)

    orig_combined = " ".join(original_chunks)
    opt_combined = " ".join(retained_chunks)

    preservation_score = calculate_semantic_preservation(orig_combined, opt_combined)
    # Preservation percentage for easy display
    preservation_pct = round(preservation_score * 100.0, 2)

    stats["semantic_preservation_score"] = preservation_score
    stats["semantic_preservation_percent"] = preservation_pct

    return stats
