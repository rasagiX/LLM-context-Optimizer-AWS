"""
Integration tests for FastAPI endpoints.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["service"] == "ai-context-compiler"


def test_optimize_demo_endpoint():
    res = client.get("/api/v1/optimize/demo")
    assert res.status_code == 200
    data = res.json()
    assert data["original_tokens"] > 0
    assert data["optimized_tokens"] < data["original_tokens"]
    assert data["reduction_percent"] > 0
    assert len(data["steps_applied"]) >= 3
    assert data["tokens_saved"] > 0
    assert "optimization_latency_ms" in data


def test_post_optimize_endpoint():
    payload = {
        "question": "What is the capital of France?",
        "conversation": [],
        "documents": [
            {"id": "doc1", "content": "Please note that Paris is the capital of France."},
            {"id": "doc2", "content": "Please note that Paris is the capital of France."}
        ],
        "tools": []
    }
    res = client.post("/api/v1/optimize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["original_tokens"] > 0
    assert data["reduction_percent"] > 0
    assert "deduplicator" in data["steps_applied"]


def test_post_run_mock_mode():
    payload = {
        "question": "Recommend a cloud provider for EU PCI compliance",
        "conversation": [],
        "documents": [{"id": "d1", "content": "AWS is PCI DSS Level 1 certified in EU."}],
        "tools": [],
        "mode": "compare"
    }
    res = client.post("/api/v1/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "run_id" in data
    assert data["baseline"] is not None
    assert data["optimized"] is not None
    assert data["comparison"] is not None
