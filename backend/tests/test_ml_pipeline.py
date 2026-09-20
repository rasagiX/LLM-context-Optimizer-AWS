"""
test_ml_pipeline.py

Unit tests for the complete ML context compiler package:
    - Selective token compressor (heuristic & semantic)
    - Two-stage reranker
    - ML Quality & Semantic preservation evaluator
    - Vector tool selector
    - Parallel embedder
"""

import pytest
import numpy as np

from ml.token_compressor import compress_tokens, compress_tokens_heuristic, compress_tokens_semantic
from ml.reranker import rerank_chunks
from ml.evaluator import calculate_semantic_preservation, evaluate_optimization
from ml.pruner import prune_context
from app.optimizer import tool_selector, prompt_compressor


def test_token_compressor_heuristic():
    text = "In order to ensure PCI-DSS Level 1 compliance, basically you must conduct an investigation of logs."
    compressed = compress_tokens_heuristic(text)

    assert "PCI-DSS Level 1" in compressed
    assert "in order to" not in compressed.lower()
    assert "basically" not in compressed.lower()
    assert len(compressed) < len(text)


def test_token_compressor_semantic():
    text = "AWS provides PCI-DSS compliance for payment cards. Today's weather in Paris is sunny."
    query = "What is the compliance standard for payment processing on AWS?"

    compressed = compress_tokens_semantic(text, query=query)
    assert "PCI-DSS" in compressed


def test_reranker():
    query = "What are the cardiovascular risks of ibuprofen?"
    chunks = [
        "The Eiffel tower was built in 1889.",
        "Long-term use of ibuprofen increases the risk of heart attack and stroke.",
        "Python is a popular programming language.",
    ]

    results = rerank_chunks(query, chunks, top_k=2)
    assert len(results) > 0
    top_chunk, top_score = results[0]
    assert "heart attack" in top_chunk
    assert top_score > 0.0


def test_evaluator():
    orig_text = "AWS supports PCI-DSS Level 1 compliance and GDPR data residency in EU regions."
    opt_text = "AWS supports PCI-DSS Level 1 and GDPR data residency in EU."

    score = calculate_semantic_preservation(orig_text, opt_text)
    assert 0.0 <= score <= 1.0
    assert score > 0.7  # High semantic retention expected

    eval_result = evaluate_optimization([orig_text], [opt_text])
    assert "semantic_preservation_score" in eval_result
    assert "reduction_percent" in eval_result


def test_semantic_tool_selector():
    tools = [
        {"name": "get_compliance_report", "description": "Fetch compliance certifications like PCI-DSS and SOC 2 for a cloud provider."},
        {"name": "order_stationery", "description": "Order pencils, notebooks, and office supplies."},
        {"name": "book_meeting_room", "description": "Book a conference room for team syncs."},
    ]
    question = "Check if AWS meets our enterprise PCI-DSS and SOC 2 security compliance needs."

    selected = tool_selector.select(tools, question, top_n=1)
    assert len(selected) == 1
    assert selected[0]["name"] == "get_compliance_report"


def test_pruner_with_reranker():
    query = "How does vaccination generate immunity?"
    chunks = [
        "Vaccines expose the immune system to antigens, building memory antibodies.",
        "Stock markets experienced heavy trading volume yesterday.",
        "The recipe requires flour, sugar, and cocoa powder.",
    ]

    result = prune_context(query, chunks, top_k=1, use_reranker=True)
    assert result["retained_count"] == 1
    assert "immune system" in result["ranked_chunks"][0]


def test_prompt_compressor_stage3():
    text = "Please note that in order to configure AWS, essentially you must set the region."
    compressed = prompt_compressor.compress(text)

    assert "please note that" not in compressed.lower()
    assert "essentially" not in compressed.lower()
    assert "AWS" in compressed
