"""
ML/NLP package for LLM Context Optimizer.

Public interface — everything the backend needs is importable from here:

    Pruning (primary use case):
        from ml import prune_context
        from ml import prune_context_from_text

    Near-duplicate detection:
        from ml import deduplicate_texts
        from ml import deduplicate_by_embedding

    Reranking & Token Compression:
        from ml import rerank_chunks
        from ml import compress_tokens

    Tool & Schema Minification:
        from ml import minify_tools
        from ml import minify_tool_to_ts

    Evaluation & ML Metrics:
        from ml import calculate_semantic_preservation
        from ml import evaluate_optimization

    Async versions (use from FastAPI route handlers):
        from ml import embed_async
        from ml import embed_query_async

    Token accounting:
        from ml import count_tokens, token_reduction_stats
"""

from ml.pruner import prune_context, prune_context_from_text
from ml.deduplicator import deduplicate_by_embedding, deduplicate_texts
from ml.embedder import embed_async, embed_query_async
from ml.utils import count_tokens, token_reduction_stats
from ml.token_compressor import compress_tokens
from ml.reranker import rerank_chunks
from ml.evaluator import calculate_semantic_preservation, evaluate_optimization
from ml.schema_minifier import minify_tools, minify_tool_to_ts

__all__ = [
    # pruning
    "prune_context",
    "prune_context_from_text",
    # deduplication
    "deduplicate_by_embedding",
    "deduplicate_texts",
    # reranking & token compression
    "rerank_chunks",
    "compress_tokens",
    # schema minification
    "minify_tools",
    "minify_tool_to_ts",
    # evaluation
    "calculate_semantic_preservation",
    "evaluate_optimization",
    # async embedding
    "embed_async",
    "embed_query_async",
    # token accounting
    "count_tokens",
    "token_reduction_stats",
]
