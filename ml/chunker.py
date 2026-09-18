"""
chunker.py

Responsible for splitting raw input text into smaller segments (chunks)
before embedding and scoring.

Why chunking matters:
    - LLMs and embedding models work better with focused, short passages
    - Chunking too large → embeddings average out and lose specificity
    - Chunking too small → chunks lose enough context to be meaningful
    - This module provides multiple strategies so we can experiment

Current strategies:
    - sentence  : split on sentence boundaries (default, good for most cases)
    - paragraph : split on blank lines
    - fixed     : split into fixed-size token windows with optional overlap
"""

import re
from typing import List


def chunk_by_sentence(text: str, min_length: int = 20) -> List[str]:
    """
    Split text into individual sentences.

    Args:
        text:       Raw input string.
        min_length: Minimum character length for a chunk to be kept.
                    Filters out fragments like "Ok." or "Yes."

    Returns:
        List of sentence strings.
    """
    raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in raw_sentences if len(s.strip()) >= min_length]


def chunk_by_paragraph(text: str, min_length: int = 30) -> List[str]:
    """
    Split text on blank lines (paragraph boundaries).

    Args:
        text:       Raw input string.
        min_length: Minimum character length to keep a paragraph.

    Returns:
        List of paragraph strings.
    """
    paragraphs = re.split(r'\n\s*\n', text.strip())
    return [p.strip() for p in paragraphs if len(p.strip()) >= min_length]


def chunk_by_fixed_size(
    text: str,
    chunk_size: int = 100,
    overlap: int = 20
) -> List[str]:
    """
    Split text into fixed-size windows measured in words, with optional overlap.

    Overlap helps preserve context at chunk boundaries — a sentence that
    starts at the end of chunk N will also appear at the start of chunk N+1.

    Args:
        text:       Raw input string.
        chunk_size: Number of words per chunk.
        overlap:    Number of words shared between consecutive chunks.

    Returns:
        List of text chunks.
    """
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


def chunk_text(
    text: str,
    strategy: str = "sentence",
    **kwargs
) -> List[str]:
    """
    Main entry point. Dispatches to the chosen chunking strategy.

    Args:
        text:     Raw input text to chunk.
        strategy: One of "sentence", "paragraph", "fixed".
        **kwargs: Extra arguments forwarded to the chosen strategy function.

    Returns:
        List of text chunk strings.

    Raises:
        ValueError: If an unknown strategy is provided.
    """
    strategies = {
        "sentence":  chunk_by_sentence,
        "paragraph": chunk_by_paragraph,
        "fixed":     chunk_by_fixed_size,
    }

    if strategy not in strategies:
        raise ValueError(
            f"Unknown chunking strategy '{strategy}'. "
            f"Choose from: {list(strategies.keys())}"
        )

    return strategies[strategy](text, **kwargs)
