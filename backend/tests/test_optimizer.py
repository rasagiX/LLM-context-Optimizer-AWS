"""
Unit tests for the 5-step Context Compiler optimizer pipeline.
"""

from app.optimizer import (
    context_pruner,
    deduplicator,
    history_compressor,
    prompt_compressor,
    tool_selector,
)
from app.optimizer.pipeline import OptimizerContext, run as run_pipeline


def test_history_compressor():
    # 8 turns (> 6 limit) should collapse older turns into a summary
    conversation = [
        {"role": "user", "content": "I need to deploy a payments microservice."},
        {"role": "assistant", "content": "What are your requirements?"},
        {"role": "user", "content": "It must be PCI-DSS compliant."},
        {"role": "assistant", "content": "Understood."},
        {"role": "user", "content": "We also need EU GDPR residency."},
        {"role": "assistant", "content": "Got it."},
        {"role": "user", "content": "Our team knows AWS well."},
        {"role": "assistant", "content": "AWS is a good choice."},
    ]
    compressed = history_compressor.compress(conversation, question="Which cloud provider should we use?")
    assert len(compressed) < len(conversation)
    assert compressed[0]["role"] == "system"
    assert "Conversation summary" in compressed[0]["content"]


def test_deduplicator():
    documents = [
        {"id": "doc1", "content": "AWS compliance includes PCI-DSS Level 1 and SOC 2 Type II."},
        {"id": "doc1_dup", "content": "AWS compliance includes PCI-DSS Level 1 and SOC 2 Type II."},
    ]
    deduped = deduplicator.dedupe(documents)
    assert len(deduped) == 1
    assert deduped[0]["id"] == "doc1"


def test_prompt_compressor():
    raw_text = "Please note that AWS is PCI compliant. As mentioned above, it is secure."
    compressed = prompt_compressor.compress(raw_text)
    assert "Please note that" not in compressed
    assert "As mentioned above" not in compressed
    assert "AWS is PCI compliant" in compressed


def test_tool_selector():
    tools = [
        {"name": "get_compliance", "description": "Fetch compliance certs for cloud providers"},
        {"name": "order_pizza", "description": "Order pepperoni pizza for lunch"},
    ]
    question = "Which cloud provider meets PCI compliance standards?"
    selected = tool_selector.select(tools, question)
    assert len(selected) == 1
    assert selected[0]["name"] == "get_compliance"


def test_pipeline_end_to_end():
    ctx = OptimizerContext(
        question="Which cloud provider should we choose for payments?",
        conversation=[
            {"role": "user", "content": "We need PCI compliance."},
            {"role": "assistant", "content": "AWS has PCI Level 1."},
        ],
        documents=[
            {"id": "aws", "content": "Please note that AWS supports PCI-DSS Level 1 compliance."},
            {"id": "aws_dup", "content": "Please note that AWS supports PCI-DSS Level 1 compliance."},
            {"id": "lunch", "content": "Today cafeteria menu features pasta and salad."},
        ],
        tools=[
            {"name": "get_compliance", "description": "Get cloud compliance info"},
            {"name": "book_flight", "description": "Book a flight to Paris"},
        ],
    )
    result = run_pipeline(ctx)
    assert "deduplicator" in result.steps_applied
    assert "tool_selector" in result.steps_applied
    assert len(result.context.documents) < 3
    assert len(result.context.tools) == 1
