"""
Prompt Compressor.

Multi-stage compression that removes token waste without changing semantic meaning:
    Stage 1 — Filler phrase removal & preamble removal
    Stage 2 — Selective ML token & clause compression (via ml.token_compressor)
    Stage 3 — Sentence-level deduplication
    Stage 4 — Whitespace normalisation
"""

import logging
import re
from typing import List

logger = logging.getLogger(__name__)

_FILLER_PATTERNS: list[str] = [
    r"\bplease note that\b",
    r"\bit is important to (?:note|mention|remember|highlight|emphasize|point out) that\b",
    r"\bas (?:mentioned|stated|noted|described|outlined|discussed) (?:above|earlier|before|previously|below)\b",
    r"\bfor your (?:information|reference|convenience)\b",
    r"\bit should be noted that\b",
    r"\bkindly (?:note|be aware) that\b",
    r"\bi would like to (?:note|mention|point out) that\b",
    r"\bfeel free to\b",
    r"\bdon't hesitate to\b",
    r"\bthank you for (?:your patience|reading|your time)\b",
    r"\bin (?:summary|conclusion|closing),?\s",
    r"\bto summarize,?\s",
    r"\bto conclude,?\s",
]

_PREAMBLE_PATTERNS: list[str] = [
    r"^(?:This document|This section|This article|The following) (?:provides|describes|contains|outlines|explains|covers) [^.]+\.\s*",
    r"^(?:Below|The following) (?:is|are) [^:]+:\s*",
    r"^(?:Overview|Introduction|Background|Preamble):\s*",
]

_LIST_PREAMBLE_PATTERNS: list[str] = [
    r"(?:Here is|Here are|The following is|The following are) (?:a list of|an overview of|a summary of)\s+",
    r"(?:Please find|You can find) (?:below|above|here) (?:a list of|the list of|an overview of)\s+",
]

_FILLER_RE = [re.compile(p, re.IGNORECASE) for p in _FILLER_PATTERNS]
_PREAMBLE_RE = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in _PREAMBLE_PATTERNS]
_LIST_RE = [re.compile(p, re.IGNORECASE) for p in _LIST_PREAMBLE_PATTERNS]


def _remove_duplicate_sentences(text: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    seen: set[str] = set()
    unique: list[str] = []
    for s in sentences:
        normalised = " ".join(s.split()).lower()
        if normalised and normalised not in seen:
            seen.add(normalised)
            unique.append(s)
    return " ".join(unique)


def _compress_tokens(text: str, question: str = "") -> str:
    try:
        from ml.token_compressor import compress_tokens
        return compress_tokens(text, query=question)
    except Exception as exc:
        logger.debug("[prompt_compressor] ML token compressor unavailable: %s", exc)
        return text


def compress(text: str, question: str = "") -> str:
    """
    Return a compressed version of text with filler, preambles, and
    redundant whitespace removed.
    """
    if not text or not text.strip():
        return text

    compressed = text

    for pattern in _FILLER_RE:
        compressed = pattern.sub("", compressed)

    for pattern in _PREAMBLE_RE:
        compressed = pattern.sub("", compressed)

    for pattern in _LIST_RE:
        compressed = pattern.sub("", compressed)

    compressed = _compress_tokens(compressed, question=question)
    compressed = _remove_duplicate_sentences(compressed)

    compressed = re.sub(r"[ \t]+", " ", compressed)
    compressed = re.sub(r"\n{3,}", "\n\n", compressed)
    compressed = re.sub(r" \n", "\n", compressed)
    compressed = re.sub(r"\n ", "\n", compressed)

    return compressed.strip()
