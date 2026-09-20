"""
Tool Selector.

Semantic Vector & Keyword Tool Selector.

Uses vector embedding similarity (via the ml package) to score candidate tools
against the user's question, keeping top-N relevant tool schemas.

If ML dependencies are unavailable, falls back to keyword overlap.
"""

import logging
import re

logger = logging.getLogger(__name__)

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "in", "on", "of", "to",
    "and", "or", "for", "with", "what", "how", "why", "does", "do", "did",
}


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def _select_semantic(tools: list[dict], question: str, top_n: int = 5, threshold: float = 0.15) -> list[dict]:
    from ml.embedder import embed
    from ml.scorer import score_chunks

    tool_texts = [
        f"Tool: {tool.get('name', '')}. Description: {tool.get('description', '')}"
        for tool in tools
    ]

    q_vec = embed([question])[0]
    t_vecs = embed(tool_texts)
    scores = score_chunks(q_vec, t_vecs).tolist()

    indexed = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

    # Filter out tools below semantic threshold unless no tool meets threshold
    kept = [tools[idx] for idx, s in indexed if s >= threshold]
    if not kept and indexed:
        kept = [tools[indexed[0][0]]]

    return kept[:top_n]


def _select_keyword(tools: list[dict], question: str, top_n: int = 5) -> list[dict]:
    q_keywords = _keywords(question)
    if not q_keywords:
        return tools[:top_n]

    scored = []
    for tool in tools:
        tool_text = f"{tool.get('name', '')} {tool.get('description', '')}"
        overlap = len(q_keywords & _keywords(tool_text))
        scored.append((overlap, tool))

    scored.sort(key=lambda pair: pair[0], reverse=True)

    best_score = scored[0][0] if scored else 0
    if best_score > 0:
        kept = [(s, t) for s, t in scored if s > 0]
    else:
        kept = scored

    return [tool for _, tool in kept[:top_n]]


def select(tools: list[dict], question: str, top_n: int = 5) -> list[dict]:
    """
    Select the most relevant tools for a given question using ML vector similarity.

    Args:
        tools: List of tool schema dicts.
        question: User query string.
        top_n: Maximum tools to retain.

    Returns:
        Filtered list of tool dicts.
    """
    if not tools:
        return tools

    if not question or not question.strip():
        return tools[:top_n]

    try:
        return _select_semantic(tools, question, top_n=top_n)
    except Exception as exc:
        logger.debug("[tool_selector] ML selection failed (%s) — falling back to keyword selection", exc)
        return _select_keyword(tools, question, top_n=top_n)
