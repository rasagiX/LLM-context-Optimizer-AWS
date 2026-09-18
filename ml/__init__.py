"""
ML/NLP package for LLM Context Optimizer.

Public interface — everything the backend needs is importable from here:

    Pruning (primary use case):
        from ml import prune_context
        from ml import prune_context_from_text

    Near-duplicate detection:
        from ml import deduplicate_texts
        from ml import deduplicate_by_embedding

    Async versions (use from FastAPI route handlers):
        from ml import embed_async
        from ml import embed_query_async

    Token accounting:
        from ml import token_reduction_stats
"""

from ml.pruner import prune_context, prune_context_from_text
from ml.deduplicator import deduplicate_by_embedding, deduplicate_texts
from ml.embedder import embed_async, embed_query_async
from ml.utils import token_reduction_stats

__all__ = [
    # pruning
    "prune_context",
    "prune_context_from_text",
    # deduplication
    "deduplicate_by_embedding",
    "deduplicate_texts",
    # async embedding
    "embed_async",
    "embed_query_async",
    # token accounting
    "token_reduction_stats",
]
