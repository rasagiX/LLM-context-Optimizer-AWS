"""
Prompt Compressor.

Multi-pass compression that aggressively removes token waste without
changing the semantic meaning of the document:

  Pass 1 — Filler phrase removal: strips hedging/boilerplate phrases.
  Pass 2 — Redundant preamble removal: strips "In this document/section..."
            openers that add no information.
  Pass 3 — List normalisation: collapses verbose bullet list preambles.
  Pass 4 — Whitespace normalisation: collapses repeated spaces/newlines.
  Pass 5 — Sentence-level deduplication: removes exact-duplicate sentences
            that sometimes appear when the same fact is restated verbatim.

All passes are regex-based and meaning-preserving — no rewriting of
content words. An LLM rewrite pass (LLMLingua-style) can be layered on
top of this for additional savings if latency budget allows.
"""

import re

# ---------------------------------------------------------------------------
# Pass 1: Filler phrases (case-insensitive, stripped with surrounding space)
# ---------------------------------------------------------------------------
_FILLER_PATTERNS: list[str] = [
    r"\bplease note that\b",
    r"\bit is important to (?:note|mention|remember|highlight) that\b",
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

# ---------------------------------------------------------------------------
# Pass 2: Redundant document preambles
# ---------------------------------------------------------------------------
_PREAMBLE_PATTERNS: list[str] = [
    r"^(?:This document|This section|This article|The following) (?:provides|describes|contains|outlines|explains|covers) [^.]+\.\s*",
    r"^(?:Below|The following) (?:is|are) [^:]+:\s*",
    r"^(?:Overview|Introduction|Background|Preamble):\s*",
]

# ---------------------------------------------------------------------------
# Pass 3: Verbose list preambles
# ---------------------------------------------------------------------------
_LIST_PREAMBLE_PATTERNS: list[str] = [
    r"(?:Here is|Here are|The following is|The following are) (?:a list of|an overview of|a summary of)\s+",
    r"(?:Please find|You can find) (?:below|above|here) (?:a list of|the list of|an overview of)\s+",
]

# Compile all patterns once at import time.
_FILLER_RE = [re.compile(p, re.IGNORECASE) for p in _FILLER_PATTERNS]
_PREAMBLE_RE = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in _PREAMBLE_PATTERNS]
_LIST_RE = [re.compile(p, re.IGNORECASE) for p in _LIST_PREAMBLE_PATTERNS]


def _remove_duplicate_sentences(text: str) -> str:
    """Remove consecutive exact-duplicate sentences."""
    # Split on sentence boundaries: period/exclamation/question followed by space or end.
    sentences = re.split(r"(?<=[.!?])\s+", text)
    seen: set[str] = set()
    unique: list[str] = []
    for s in sentences:
        normalised = " ".join(s.split()).lower()
        if normalised and normalised not in seen:
            seen.add(normalised)
            unique.append(s)
    return " ".join(unique)


def compress(text: str) -> str:
    """
    Return a compressed version of text with filler, preambles, and
    redundant whitespace removed. The input is never lengthened.
    """
    if not text or not text.strip():
        return text

    compressed = text

    # Pass 1: filler phrases
    for pattern in _FILLER_RE:
        compressed = pattern.sub("", compressed)

    # Pass 2: redundant preambles (multiline, anchored to line start)
    for pattern in _PREAMBLE_RE:
        compressed = pattern.sub("", compressed)

    # Pass 3: verbose list preambles
    for pattern in _LIST_RE:
        compressed = pattern.sub("", compressed)

    # Pass 4: whitespace normalisation
    compressed = re.sub(r"[ \t]+", " ", compressed)       # collapse inline spaces
    compressed = re.sub(r"\n{3,}", "\n\n", compressed)    # max two consecutive newlines
    compressed = re.sub(r" \n", "\n", compressed)          # trailing space before newline
    compressed = re.sub(r"\n ", "\n", compressed)          # leading space after newline

    # Pass 5: sentence-level deduplication
    compressed = _remove_duplicate_sentences(compressed)

    return compressed.strip()
