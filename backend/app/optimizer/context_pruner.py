"""
Context Pruner.

Uses semantic embedding similarity (via the ml/ package) to score each
document against the question and keep only the most relevant ones.

Falls back to TF-IDF weighted cosine similarity if sentence-transformers / Bedrock
embedding is unavailable.
"""

import logging
import math
import re
from collections import Counter
import numpy as np

logger = logging.getLogger(__name__)

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "in", "on", "of", "to",
    "and", "or", "for", "with", "what", "how", "why", "does", "do", "did",
    "this", "that", "it", "be", "as", "at", "by", "we", "you", "i", "he",
    "she", "they", "its", "our", "your", "their", "will", "can", "has",
    "have", "had", "not", "but", "so", "if", "than", "then", "from",
}


# --------------------------------------------------------------------------
# Semantic pruning (primary path)
# --------------------------------------------------------------------------

def _prune_semantic(
    documents: list[dict],
    question: str,
    top_k: int = -1,
    threshold: float = 0.2,
) -> list[dict]:
    from ml.embedder import embed
    from ml.scorer import score_chunks

    contents = [doc.get("content", "") for doc in documents]

    query_vector = embed([question])[0]
    chunk_vectors = embed(contents)

    scores = score_chunks(query_vector, chunk_vectors)
    score_list = scores.tolist()

    indexed = sorted(enumerate(score_list), key=lambda x: x[1], reverse=True)
    kept = [(i, s) for i, s in indexed if s >= threshold]

    if top_k > 0:
        kept = kept[:top_k]

    if not kept and score_list:
        best_idx = max(range(len(score_list)), key=lambda i: score_list[i])
        kept = [(best_idx, score_list[best_idx])]

    result = [documents[i] for i, _ in kept]
    logger.debug(
        "[context_pruner] semantic: %d -> %d documents (threshold=%.2f)",
        len(documents), len(result), threshold,
    )
    return result


# --------------------------------------------------------------------------
# TF-IDF fallback (used only when ml deps are missing)
# --------------------------------------------------------------------------

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


def _prune_tfidf(documents: list[dict], question: str, min_score: float = 0.05) -> list[dict]:
    if not documents:
        return documents

    q_tokens = _tokenize(question)
    if not q_tokens:
        return documents

    doc_tokens_list = [_tokenize(doc.get("content", "")) for doc in documents]
    idf = _idf(doc_tokens_list)
    q_vector = _tfidf_vector(_tf(q_tokens), idf)

    scored: list[tuple[float, dict]] = []
    for doc, doc_tokens in zip(documents, doc_tokens_list):
        doc_vector = _tfidf_vector(_tf(doc_tokens), idf)
        score = _cosine_similarity(q_vector, doc_vector)
        scored.append((score, doc))

    kept = [doc for score, doc in scored if score >= min_score]
    if not kept and scored:
        kept = [max(scored, key=lambda pair: pair[0])[1]]
    return kept


def prune(
    documents: list[dict],
    question: str,
    top_k: int = -1,
    threshold: float = 0.2,
) -> list[dict]:
    """
    Remove documents that are not semantically relevant to the question.
    """
    if not documents or not question or not question.strip():
        return documents

    try:
        return _prune_semantic(documents, question, top_k=top_k, threshold=threshold)
    except Exception as exc:
        logger.warning(
            "[context_pruner] semantic pruning unavailable (%s) — falling back to TF-IDF", exc
        )
        return _prune_tfidf(documents, question)
