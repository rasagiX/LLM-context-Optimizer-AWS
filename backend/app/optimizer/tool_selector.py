"""
Tool Selector.

Baseline implementation: keyword overlap between the question and each
tool's name/description. Keeps the top-N most relevant tools instead of
sending the full tool schema list to the model.

TODO: replace with an LLM-based tool router for cases where relevance
isn't lexically obvious (e.g. "check on that" implying a calendar tool).
"""

import re

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "in", "on", "of", "to",
    "and", "or", "for", "with", "what", "how", "why", "does", "do", "did",
}


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def select(tools: list[dict], question: str, top_n: int = 5) -> list[dict]:
    if not tools:
        return tools

    q_keywords = _keywords(question)
    if not q_keywords:
        return tools[:top_n]

    scored = []
    for tool in tools:
        tool_text = f"{tool.get('name', '')} {tool.get('description', '')}"
        overlap = len(q_keywords & _keywords(tool_text))
        scored.append((overlap, tool))

    scored.sort(key=lambda pair: pair[0], reverse=True)

    # If any tools have non-zero overlap, drop zero-overlap tools
    # (they are clearly irrelevant). Always keep at least 1 tool.
    best_score = scored[0][0] if scored else 0
    if best_score > 0:
        kept = [(s, t) for s, t in scored if s > 0]
    else:
        kept = scored

    return [tool for _, tool in kept[:top_n]]
