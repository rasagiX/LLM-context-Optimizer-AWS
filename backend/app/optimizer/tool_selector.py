"""
Tool Selector.

Semantic Vector & TF-IDF Tool Selector.
Uses vector embedding similarity to score candidate tools against the user's question,
falling back to TF-IDF weighted cosine similarity if ML is offline.
"""

import logging
import math
import re
from collections import Counter

logger = logging.getLogger(__name__)

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
    kept = [tools[idx] for idx, s in indexed if s >= threshold]
    if not kept and indexed:
        kept = [tools[indexed[0][0]]]

    return kept[:top_n]


def _select_tfidf(tools: list[dict], question: str, top_n: int = 5) -> list[dict]:
    q_tokens = _tokenize(question)
    if not q_tokens:
        return tools[:top_n]

    tool_tokens_list = [
        _tokenize(f"{tool.get('name', '')} {tool.get('description', '')}")
        for tool in tools
    ]
    idf = _idf(tool_tokens_list)
    q_vector = _tfidf_vector(_tf(q_tokens), idf)

    scored: list[tuple[float, dict]] = []
    for tool, tool_tokens in zip(tools, tool_tokens_list):
        tool_vector = _tfidf_vector(_tf(tool_tokens), idf)
        score = _cosine_similarity(q_vector, tool_vector)
        scored.append((score, tool))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    best_score = scored[0][0] if scored else 0
    if best_score > 0:
        kept = [t for s, t in scored if s > 0]
    else:
        kept = [t for _, t in scored]

    return kept[:top_n]


def select(tools: list[dict], question: str, top_n: int = 5) -> list[dict]:
    """
    Select the most relevant tools for a given question.
    """
    if not tools:
        return tools

    if not question or not question.strip():
        return tools[:top_n]

    try:
        return _select_semantic(tools, question, top_n=top_n)
    except Exception as exc:
        logger.debug("[tool_selector] ML selection failed (%s) — falling back to TF-IDF", exc)
        return _select_tfidf(tools, question, top_n=top_n)
