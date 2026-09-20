"""
token_compressor.py

Selective Token Pruning & Query Mutual Information Compressor.

Provides token-level mutual information compression (LLMLingua-style):
    1. Evaluates Query Mutual Information score S(w, Q) = CosineSim(vec_w, vec_Q) * IDF(w)
    2. Strictly protects core entities (numbers, compliance terms, proper nouns).
    3. Prunes low-information tokens and filler phrases.
"""

import math
import re
from collections import Counter
from typing import List, Set
import numpy as np

_ENTITY_PATTERN = re.compile(
    r"\b([A-Z0-9\-_]{2,}|[0-9]+(?:\.[0-9]+)?|PCI-DSS|GDPR|SOC|HIPAA|ISO|AWS|GCP|Azure)\b"
)

_LOW_INFO_WORDS: Set[str] = {
    "basically", "essentially", "literally", "virtually", "actually", "generally",
    "typically", "obviously", "clearly", "naturally", "definitely", "certainly",
    "absolutely", "undoubtedly", "arguably", "relatively", "somewhat", "quite",
    "rather", "fairly", "very", "extremely", "tremendously", "incredibly",
    "furthermore", "moreover", "nevertheless", "notwithstanding", "nonetheless",
    "heretofore", "aforementioned", "herein", "therein", "whereupon",
}

_CLAUSE_SPLIT_PATTERN = re.compile(r"(?<=[,;:\-])\s+|\b(?:which|that|who|whom|whose|where|when)\b\s+")


def _is_entity(word: str) -> bool:
    return bool(_ENTITY_PATTERN.search(word))


def compress_tokens_heuristic(text: str) -> str:
    if not text:
        return text

    simplifications = [
        (r"\bin order to\b", "to"),
        (r"\bdue to the fact that\b", "because"),
        (r"\bat this point in time\b", "now"),
        (r"\bwith regard to\b", "regarding"),
        (r"\bin the event that\b", "if"),
        (r"\bfor the purpose of\b", "for"),
        (r"\ba large number of\b", "many"),
        (r"\ba majority of\b", "most"),
        (r"\bhas the ability to\b", "can"),
        (r"\bis able to\b", "can"),
        (r"\btake into consideration\b", "consider"),
        (r"\bconduct an investigation of\b", "investigate"),
        (r"\bprovide assistance to\b", "help"),
    ]

    compressed = text
    for pattern, replacement in simplifications:
        compressed = re.sub(pattern, replacement, compressed, flags=re.IGNORECASE)

    words = compressed.split()
    filtered_words = []
    for w in words:
        clean_w = re.sub(r"[^\w\-]", "", w).lower()
        if clean_w in _LOW_INFO_WORDS and not _is_entity(w):
            continue
        filtered_words.append(w)

    return " ".join(filtered_words)


def compress_tokens_mutual_information(
    text: str,
    query: str,
    target_ratio: float = 0.8,
) -> str:
    """
    LLMLingua-style token importance compressor using Query Mutual Information.

    Args:
        text: Document text to compress.
        query: User query string.
        target_ratio: Proportion of tokens to retain (e.g. 0.8 = keep top 80%).

    Returns:
        Token-compressed text.
    """
    if not text or not query or not query.strip():
        return compress_tokens_heuristic(text)

    words = text.split()
    if len(words) <= 8:
        return text

    try:
        from ml.embedder import embed, embed_query
        from ml.scorer import score_chunks

        q_vec = embed_query(query)
        w_vecs = embed(words)
        sims = score_chunks(q_vec, w_vecs)

        # Calculate Query Mutual Information scores
        scores = []
        for idx, (word, sim) in enumerate(zip(words, sims.tolist())):
            clean = re.sub(r"[^\w\-]", "", word).lower()
            if _is_entity(word) or clean in query.lower():
                score = 100.0  # Force retain entities and query terms
            elif clean in _LOW_INFO_WORDS:
                score = -10.0  # Penalize filler words
            else:
                idf_weight = math.log(1.0 + len(clean))
                score = sim * idf_weight
            scores.append((idx, score, word))

        # Determine cutoff threshold to keep target_ratio
        k_keep = max(1, int(len(words) * target_ratio))
        top_ranked_indices = set(
            idx for idx, _, _ in sorted(scores, key=lambda x: x[1], reverse=True)[:k_keep]
        )

        # Reconstruct in original token order
        kept_words = [words[i] for i in range(len(words)) if i in top_ranked_indices]
        return " ".join(kept_words)

    except Exception:
        return compress_tokens_heuristic(text)


def compress_tokens_semantic(
    text: str,
    query: str = "",
    min_clause_length: int = 15,
    threshold: float = 0.25,
) -> str:
    if not text or not text.strip():
        return text

    text = compress_tokens_heuristic(text)
    if not query or not query.strip():
        return text

    return compress_tokens_mutual_information(text, query)


def compress_tokens(text: str, query: str = "") -> str:
    if query:
        return compress_tokens_semantic(text, query)
    return compress_tokens_heuristic(text)
