"""
Tool Selector.

Scores each tool's relevance to the question using TF-IDF-weighted cosine
similarity (same approach as context_pruner). Keeps the top-N tools.

This is a significant upgrade over raw keyword overlap: tools with common
words in their descriptions are not over-promoted, and tools that share
rare, specific terms with the question are correctly ranked higher.
"""

import math
import re
from collections import Counter

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "in", "on", "of", "to",
    "and", "or", "for", "with", "what", "how", "why", "does", "do", "did",
    "this", "that", "it", "be", "as", "at", "by", "we", "you", "i", "he",
    "she", "they", "its", "our", "your", "their", "will", "can", "has",
    "have", "had", "not", "but", "so", "if", "than", "then", "from",
    "get", "set", "use", "returns", "return", "given", "used",
}


def _tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def _tf(tokens: list[str]) -> dict[str, float]:
    if not tokens:
        return {}
    counts = Counter(tokens)
    max_count = max(counts.values())
    return {term: count / max_count for term, count in counts.items()}


def _idf(documents_tokens: list[list[str]]) -> dict[str, float]:
    n = len(documents_tokens)
    if n == 0:
        return {}
    df: dict[str, int] = {}
    for tokens in documents_tokens:
        for term in set(tokens):
            df[term] = df.get(term, 0) + 1
    return {term: math.log((n + 1) / (count + 1)) + 1 for term, count in df.items()}


def _tfidf_vector(tf: dict[str, float], idf: dict[str, float]) -> dict[str, float]:
    return {term: tf_val * idf.get(term, 1.0) for term, tf_val in tf.items()}


def _cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    if not vec_a or not vec_b:
        return 0.0
    dot = sum(vec_a.get(t, 0.0) * vec_b.get(t, 0.0) for t in vec_b)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def select(tools: list[dict], question: str, top_n: int = 5) -> list[dict]:
    """
    Return the top_n most relevant tools for the question, ranked by
    TF-IDF cosine similarity. If the question yields no tokens (e.g. empty
    string) or fewer tools than top_n exist, returns tools[:top_n] as-is.
    """
    if not tools:
        return tools

    q_tokens = _tokenize(question)
    if not q_tokens:
        return tools[:top_n]

    # Build the tool text corpus for IDF.
    tool_texts = [
        _tokenize(f"{tool.get('name', '')} {tool.get('description', '')}")
        for tool in tools
    ]
    idf = _idf(tool_texts)
    q_vector = _tfidf_vector(_tf(q_tokens), idf)

    scored: list[tuple[float, dict]] = []
    for tool, tool_tokens in zip(tools, tool_texts):
        tool_vector = _tfidf_vector(_tf(tool_tokens), idf)
        score = _cosine_similarity(q_vector, tool_vector)
        scored.append((score, tool))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [tool for _, tool in scored[:top_n]]
