"""
Context Pruner.

Baseline implementation: keyword-overlap relevance scoring between the
question and each document, keeping only documents above a threshold.

TODO: replace with embedding similarity or an LLM relevance classifier
once the baseline is benchmarked — keyword overlap is a cheap v0 so the
pipeline is runnable end to end.
"""

import re

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "in", "on", "of", "to",
    "and", "or", "for", "with", "what", "how", "why", "does", "do", "did",
}


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def prune(documents: list[dict], question: str, min_overlap: float = 0.05) -> list[dict]:
    """
    Keep documents whose keyword overlap with the question exceeds
    min_overlap. Always keeps at least one document if any were provided,
    to avoid dropping the only available context.
    """
    if not documents:
        return documents

    q_keywords = _keywords(question)
    if not q_keywords:
        return documents

    scored = []
    for doc in documents:
        doc_keywords = _keywords(doc.get("content", ""))
        overlap = len(q_keywords & doc_keywords) / max(len(q_keywords), 1)
        scored.append((overlap, doc))

    kept = [doc for overlap, doc in scored if overlap >= min_overlap]
    if not kept:
        # Nothing cleared the bar — fall back to the single best match
        # rather than sending zero documents.
        kept = [max(scored, key=lambda pair: pair[0])[1]]

    return kept
