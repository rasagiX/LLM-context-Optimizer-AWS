"""
utils.py

Utility helpers for the ML/NLP package.

Currently contains:
    token_reduction_stats — measures how many tokens the pruner saved,
    expressed as counts and a percentage. Useful for logging, dashboards,
    and the backend's OptimizeResponse.reduction_percent field.

Token counting strategy:
    Uses tiktoken (cl100k_base, the GPT-4 / Claude tokeniser) when
    available for an accurate count. Falls back to a 4-chars-per-token
    heuristic when tiktoken is not installed. The heuristic is intentionally
    the same approach used in backend/app/optimizer/token_utils.py so the
    numbers are consistent across the stack.
"""

from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# Token counting (mirrors backend/app/optimizer/token_utils.py approach)
# ---------------------------------------------------------------------------

_encoding = None
_tiktoken_unavailable = False


def _get_encoding():
    global _encoding, _tiktoken_unavailable
    if _encoding is not None or _tiktoken_unavailable:
        return _encoding
    try:
        import tiktoken
        _encoding = tiktoken.get_encoding("cl100k_base")
    except Exception:
        _tiktoken_unavailable = True
    return _encoding


def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a string.

    Uses tiktoken cl100k_base when available; falls back to len(text)//4.

    Args:
        text: Any string.

    Returns:
        Estimated token count as an integer.
    """
    if not text:
        return 0
    enc = _get_encoding()
    if enc is not None:
        return len(enc.encode(text))
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Token reduction stats
# ---------------------------------------------------------------------------

def token_reduction_stats(
    original_chunks: List[str],
    retained_chunks: List[str],
) -> Dict[str, Any]:
    """
    Compute token counts before and after pruning and derive the reduction.

    Designed to be called right after prune_context() to give the backend
    concrete numbers for OptimizeResponse and logging.

    Args:
        original_chunks: All context chunks before pruning.
        retained_chunks: Chunks kept after pruning (i.e. ranked_chunks from
                         the prune_context() result dict).

    Returns:
        Dictionary with:
            original_tokens  (int)   – token count of all input chunks combined
            retained_tokens  (int)   – token count of kept chunks combined
            removed_tokens   (int)   – tokens saved
            reduction_percent (float) – percentage reduction (0–100), 2 d.p.
            original_count   (int)   – number of chunks before pruning
            retained_count   (int)   – number of chunks after pruning

    Example:
        >>> stats = token_reduction_stats(
        ...     original_chunks=["Long irrelevant text...", "Relevant chunk."],
        ...     retained_chunks=["Relevant chunk."],
        ... )
        >>> stats["reduction_percent"]
        78.5   # (hypothetical)
    """
    original_tokens = sum(count_tokens(c) for c in original_chunks)
    retained_tokens = sum(count_tokens(c) for c in retained_chunks)
    removed_tokens  = original_tokens - retained_tokens

    if original_tokens > 0:
        reduction_pct = round((removed_tokens / original_tokens) * 100, 2)
    else:
        reduction_pct = 0.0

    return {
        "original_tokens":   original_tokens,
        "retained_tokens":   retained_tokens,
        "removed_tokens":    removed_tokens,
        "reduction_percent": reduction_pct,
        "original_count":    len(original_chunks),
        "retained_count":    len(retained_chunks),
    }
