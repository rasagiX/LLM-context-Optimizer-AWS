"""
test_advanced_optimization.py

Unit tests for advanced token optimization features:
    - Schema minification (TS signature & compact JSON)
    - Semantic boundary chunking
    - Query Mutual Information token compression
"""

import pytest

from ml.schema_minifier import minify_tool_to_ts, minify_tool_to_json, minify_tools
from ml.chunker import chunk_by_semantic_boundaries
from ml.token_compressor import compress_tokens_mutual_information


def test_schema_minifier_ts():
    tool = {
        "name": "get_compliance_report",
        "description": "Fetch compliance reports.",
        "input_schema": {
            "type": "object",
            "properties": {
                "provider": {"type": "string"},
                "region": {"type": "string"},
            },
            "required": ["provider"],
        },
    }

    sig = minify_tool_to_ts(tool)
    assert sig == "get_compliance_report(provider: string, region?: string): Fetch compliance reports."
    assert len(sig) < 100


def test_schema_minifier_json():
    tool = {
        "name": "compare_pricing",
        "description": "Compare hourly costs.",
        "input_schema": {
            "type": "object",
            "properties": {"provider": {"type": "string"}},
        },
    }

    compact = minify_tool_to_json(tool)
    assert '"name":"compare_pricing"' in compact
    assert '"desc":"Compare hourly costs."' in compact
    assert "\n" not in compact


def test_semantic_chunking():
    text = (
        "AWS holds PCI-DSS Level 1 compliance for credit cards. It also supports GDPR data residency in EU regions. "
        "Chocolate chip cookies are best baked at 350 degrees Fahrenheit. Vanilla extract enhances cookie flavor. "
        "Python is a versatile programming language used for machine learning and data science."
    )

    chunks = chunk_by_semantic_boundaries(text, distance_threshold=0.3, min_sentences=1)
    assert len(chunks) >= 2


def test_mutual_information_token_compression():
    text = "Please note that in order to ensure PCI-DSS Level 1 compliance, AWS holds SOC 2 Type II certifications which are very useful."
    query = "What PCI-DSS and SOC 2 security certifications does AWS hold?"

    compressed = compress_tokens_mutual_information(text, query, target_ratio=0.7)
    assert "PCI-DSS" in compressed
    assert "SOC 2" in compressed
    assert len(compressed.split()) <= len(text.split())
