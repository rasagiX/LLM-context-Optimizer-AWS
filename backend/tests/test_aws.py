"""
Tests for AWS services, local mock modes, and fallbacks.
"""

from app.config import settings
from app.services import bedrock, cloudwatch, judge, s3, store


def test_bedrock_local_mock_mode():
    res = bedrock.invoke(prompt="Test prompt", system=None)
    assert res.text != ""
    assert res.input_tokens > 0
    assert res.latency_ms >= 0


def test_judge_evaluate_mock_mode():
    quality = judge.evaluate(
        question="Is AWS PCI compliant?",
        answer="Yes, AWS holds PCI-DSS Level 1 compliance.",
        rubric=["Mentions PCI compliance"]
    )
    assert quality.score >= 0.0
    assert isinstance(quality.rubric_hits, list)


def test_cloudwatch_mock_logging():
    # Should not raise any exceptions when AWS_ENABLED=False
    cloudwatch.log_pipeline_execution(
        endpoint="/test",
        original_tokens=100,
        optimized_tokens=40,
        reduction_percent=60.0,
        latency_ms=15
    )


def test_s3_and_store_local_fallback():
    run_id = "test_run_123"
    data = {"run_id": run_id, "test": True}
    store.save_run(run_id, data)
    retrieved = store.get_run(run_id)
    assert retrieved is not None
    assert retrieved["run_id"] == run_id
