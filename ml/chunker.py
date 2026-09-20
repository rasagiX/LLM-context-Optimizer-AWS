"""
chunker.py

Responsible for splitting raw input text into smaller segments (chunks)
before embedding and scoring.

Strategies:
    - sentence : split on sentence boundaries
    - paragraph: split on blank lines
    - fixed    : split into fixed-size word windows
    - semantic : split at vector embedding distance topic boundaries
"""

import re
from typing import List
import numpy as np


def chunk_by_sentence(text: str, min_length: int = 20) -> List[str]:
    raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in raw_sentences if len(s.strip()) >= min_length]


def chunk_by_paragraph(text: str, min_length: int = 30) -> List[str]:
    paragraphs = re.split(r'\n\s*\n', text.strip())
    return [p.strip() for p in paragraphs if len(p.strip()) >= min_length]


def chunk_by_fixed_size(
    text: str,
    chunk_size: int = 100,
    overlap: int = 20
) -> List[str]:
    words = text.split()
    chunks = []
    step = chunk_size - overlap

    if step <= 0:
        raise ValueError("overlap must be less than chunk_size")

    for i in range(0, len(words), step):
        window = words[i : i + chunk_size]
        if window:
            chunks.append(" ".join(window))

    return chunks


def chunk_by_semantic_boundaries(
    text: str,
    distance_threshold: float = 0.4,
    min_sentences: int = 2,
) -> List[str]:
    """
    Split text at topic transition boundaries determined by sentence embedding distance.

    Calculates cosine distance d(s_i, s_{i+1}) between consecutive sentences.
    If d >= distance_threshold, splits and starts a new semantic topic chunk.

    Args:
        text: Raw document text.
        distance_threshold: Cosine distance threshold (0.0 to 1.0) for topic split.
        min_sentences: Minimum sentences per semantic chunk.

    Returns:
        List of semantically segmented text chunks.
    """
    sentences = chunk_by_sentence(text, min_length=15)
    if len(sentences) <= min_sentences:
        return [text.strip()]

    try:
        from ml.embedder import embed
        vecs = embed(sentences)

        # Row-normalize for cosine similarity
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1e-10, norms)
        unit_vecs = vecs / norms

        chunks = []
        current_chunk_sentences = [sentences[0]]

        for i in range(len(sentences) - 1):
            sim = float(np.dot(unit_vecs[i], unit_vecs[i + 1]))
            dist = 1.0 - sim

            if dist >= distance_threshold and len(current_chunk_sentences) >= min_sentences:
                chunks.append(" ".join(current_chunk_sentences))
                current_chunk_sentences = [sentences[i + 1]]
            else:
                current_chunk_sentences.append(sentences[i + 1])

        if current_chunk_sentences:
            chunks.append(" ".join(current_chunk_sentences))

        return chunks
    except Exception:
        # Fallback to paragraph chunking if ML fails
        return chunk_by_paragraph(text)


def chunk_text(
    text: str,
    strategy: str = "sentence",
    **kwargs
) -> List[str]:
    """
    Main entry point. Dispatches to chosen chunking strategy.

    Args:
        text: Raw input text.
        strategy: "sentence", "paragraph", "fixed", or "semantic".
        **kwargs: Strategy keyword args.
    """
    strategies = {
        "sentence":  chunk_by_sentence,
        "paragraph": chunk_by_paragraph,
        "fixed":     chunk_by_fixed_size,
        "semantic":  chunk_by_semantic_boundaries,
    }

    if strategy not in strategies:
        raise ValueError(
            f"Unknown chunking strategy '{strategy}'. "
            f"Choose from: {list(strategies.keys())}"
        )

    return strategies[strategy](text, **kwargs)
