"""
Prompt Compressor.

Reduces token count in document content without changing meaning.
Uses three stages:
    Stage 1 — Filler phrase removal: strips verbose phrases that add words
              but no information ("please note that", "it is worth mentioning
              that", etc.).
    Stage 2 — Selective ML token compression: sub-sentence information entropy
              pruning and phrase simplification (via ml.token_compressor).
    Stage 3 — Whitespace normalisation: collapses repeated spaces, tabs,
              and blank lines.
"""

import logging
import re
from typing import List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stage 1 — Filler phrase patterns
# ---------------------------------------------------------------------------

_FILLER_PATTERNS: List[str] = [
    # Redundant openers
    r"\bplease note that\b",
    r"\bit is important to (note|mention|highlight|emphasize|point out) that\b",
    r"\bit should be noted that\b",
    r"\bit is worth (noting|mentioning|highlighting) that\b",
    r"\bkindly note that\b",
    r"\bplease be aware that\b",
    r"\bplease be advised that\b",
    # Redundant back-references
    r"\bas (mentioned|stated|noted|described|outlined|discussed) (above|earlier|before|previously|below)\b",
    r"\bas (we|I) (mentioned|stated|noted|discussed) (earlier|before|previously|above)\b",
    r"\bas previously (mentioned|stated|noted|discussed)\b",
    r"\bfor (your|the) (reference|information|convenience)\b",
    r"\bfor (your|the) (reference|information|convenience),?\s*",
    # Empty transitional padding
    r"\bit goes without saying that\b",
    r"\bneedless to say,?\s*",
    r"\bobviously,?\s*",
    r"\bof course,?\s*",
    r"\bclearly,?\s*",
    r"\bbasically,?\s*",
    r"\bessentially,?\s*",
    r"\bin (simple|plain|other) words,?\s*",
    r"\bto (put it simply|be (clear|honest|frank)),?\s*",
    # Verbose sign-offs
    r"\bI hope this (helps|clarifies|answers your question)\b[.!]*",
    r"\bplease (let me know|feel free to reach out|don't hesitate to ask)[^.]*\.",
    r"\bif you have any (further |more |additional )?(questions|concerns|queries)[^.]*\.",
]

_COMPILED_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in _FILLER_PATTERNS
]


def _remove_fillers(text: str) -> str:
    for pattern in _COMPILED_PATTERNS:
        text = pattern.sub("", text)
    return text


# ---------------------------------------------------------------------------
# Stage 2 — Selective ML token compression
# ---------------------------------------------------------------------------

def _compress_tokens(text: str, question: str = "") -> str:
    try:
        from ml.token_compressor import compress_tokens
        return compress_tokens(text, query=question)
    except Exception as exc:
        logger.debug("[prompt_compressor] ML token compressor unavailable: %s", exc)
        return text


# ---------------------------------------------------------------------------
# Stage 3 — Whitespace normalisation
# ---------------------------------------------------------------------------

def _normalise_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" +\n", "\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def compress(text: str, question: str = "") -> str:
    """
    Reduce token count in a document string without changing its meaning.

    Stages:
        1. Strip filler phrases
        2. ML selective token compression
        3. Normalise whitespace

    Args:
        text: Document content string.
        question: Optional user question for semantic alignment.

    Returns:
        Compressed string.
    """
    if not text:
        return text

    text = _remove_fillers(text)
    text = _compress_tokens(text, question=question)
    text = _normalise_whitespace(text)
    return text
