"""
pruner.py

The main pipeline. This is the single entry point the backend will call.

It orchestrates:
    1. (Optional) chunking of raw text into segments
    2. Embedding the query
    3. Embedding the context chunks
    4. Scoring each chunk against the query
    5. Ranking and filtering
    6. Returning the optimized context

Backend contract:
    from ml.pruner import prune_context

    result = prune_context(
        query="What are the risks of long-term ibuprofen use?",
        context_chunks=["chunk one...", "chunk two...", ...],
        top_k=5,
        threshold=0.3,
    )
"""

from typing import List, Dict, Any

from ml.embedder import embed, embed_query
from ml.scorer import score_chunks, rank_chunks
from ml.chunker import chunk_text


def prune_context(
    query: str,
    context_chunks: List[str],
    top_k: int = 5,
    threshold: float = 0.0,
) -> Dict[str, Any]:
    """
    Core pipeline: score and filter context chunks by relevance to a query.

    Args:
        query:          The user's question or input prompt.
        context_chunks: List of text segments to evaluate.
        top_k:          Number of top-scoring chunks to return. -1 = no limit.
        threshold:      Minimum cosine similarity score to keep a chunk.

    Returns:
        {
            ranked_chunks  (List[str])   – top chunks, best first
            scores         (List[float]) – corresponding similarity scores
            original_count (int)         – number of input chunks
            retained_count (int)         – number of chunks kept after filtering
        }
    """
    if not query.strip():
        raise ValueError("query must not be empty.")
    if not context_chunks:
        raise ValueError("context_chunks must not be empty.")

    original_count = len(context_chunks)

    query_vector = embed_query(query)
    chunk_vectors = embed(context_chunks)
    scores = score_chunks(query_vector, chunk_vectors)

    ranked_pairs = rank_chunks(
        chunks=context_chunks,
        scores=scores,
        top_k=top_k,
        threshold=threshold,
    )

    if ranked_pairs:
        ranked_chunks, ranked_scores = zip(*ranked_pairs)
        ranked_chunks = list(ranked_chunks)
        ranked_scores = list(ranked_scores)
    else:
        ranked_chunks = []
        ranked_scores = []

    return {
        "ranked_chunks":   ranked_chunks,
        "scores":          ranked_scores,
        "original_count":  original_count,
        "retained_count":  len(ranked_chunks),
    }


def prune_context_from_text(
    query: str,
    raw_text: str,
    chunking_strategy: str = "sentence",
    top_k: int = 5,
    threshold: float = 0.0,
    **chunker_kwargs,
) -> Dict[str, Any]:
    """
    Convenience wrapper: chunk raw text first, then run the pruning pipeline.

    Args:
        query:              The user's question.
        raw_text:           Full document or passage to prune.
        chunking_strategy:  "sentence", "paragraph", or "fixed".
        top_k:              Max chunks to return.
        threshold:          Minimum similarity score to keep a chunk.
        **chunker_kwargs:   Extra args forwarded to the chunker.

    Returns:
        Same dict as prune_context(), plus:
            chunks_before_pruning (List[str]) – all chunks produced by chunker
    """
    chunks = chunk_text(raw_text, strategy=chunking_strategy, **chunker_kwargs)
    result = prune_context(
        query=query,
        context_chunks=chunks,
        top_k=top_k,
        threshold=threshold,
    )
    result["chunks_before_pruning"] = chunks
    return result
