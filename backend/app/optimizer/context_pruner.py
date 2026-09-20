"""
Context Pruner.

Scores each document's relevance to the question using TF-IDF-weighted
cosine similarity. This is a substantial upgrade over raw keyword overlap:
it down-weights common words that appear in many documents (reducing noise)
and up-weights rare terms that are genuinely discriminative.

Algorithm:
  1. Tokenise + remove stopwords for all documents and the question.
  2. Build a corpus-level IDF table from the document set.
  3. Compute a TF-IDF vector for each document and for the question.
  4. Score each document by cosine similarity against the question vector.
  5. Keep documents above MIN_SCORE; always keep at least one.
"""

import math
import re
from collections import Counter

# Minimum cosine similarity to retain a document.
MIN_SCORE = 0.05

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "in", "on", "of", "to",
    "and", "or", "for", "with", "what", "how", "why", "does", "do", "did",
    "this", "that", "it", "be", "as", "at", "by", "we", "you", "i", "he",
    "she", "they", "its", "our", "your", "their", "will", "can", "has",
    "have", "had", "not", "but", "so", "if", "than", "then", "from",
}


def _tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def _tf(tokens: list[str]) -> dict[str, float]:
    """Term frequency: count normalised by document length."""
    if not tokens:
        return {}
    counts = Counter(tokens)
    max_count = max(counts.values())
    return {term: count / max_count for term, count in counts.items()}


def _idf(documents_tokens: list[list[str]]) -> dict[str, float]:
    """Inverse document frequency over the corpus."""
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


def prune(documents: list[dict], question: str, min_score: float = MIN_SCORE) -> list[dict]:
    """
    Return documents whose TF-IDF cosine similarity with the question
    exceeds min_score. Always returns at least one document if any were
    provided, to avoid sending zero context to the model.
    """
    if not documents:
        return documents

    q_tokens = _tokenize(question)
    if not q_tokens:
        return documents

    doc_tokens_list = [_tokenize(doc.get("content", "")) for doc in documents]

    # Build IDF over the document corpus (question excluded — it's the query).
    idf = _idf(doc_tokens_list)

    q_vector = _tfidf_vector(_tf(q_tokens), idf)

    scored: list[tuple[float, dict]] = []
    for doc, doc_tokens in zip(documents, doc_tokens_list):
        doc_vector = _tfidf_vector(_tf(doc_tokens), idf)
        score = _cosine_similarity(q_vector, doc_vector)
        scored.append((score, doc))

    kept = [doc for score, doc in scored if score >= min_score]
    if not kept:
        # Nothing cleared the bar — keep the single best match.
        kept = [max(scored, key=lambda pair: pair[0])[1]]

    return kept
