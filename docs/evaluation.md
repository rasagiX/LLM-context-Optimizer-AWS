# Evaluation & Benchmark Harness

This document describes the evaluation methodologies, benchmark suites, and LLM Quality Judge scoring used to measure the **AI Context Compiler**.

---

## 📊 Benchmark Harness (`backend/app/benchmark/`)

The benchmark harness tests the Context Compiler against a fixed suite of realistic enterprise workloads defined in `backend/app/benchmark/tasks.json`.

### Categories Covered:
1. **Multi-turn History Compression**: Conversation histories (> 10 turns) with noisy chit-chat.
2. **Document Pruning**: Mixed context with irrelevant documents (HR policies, lunch menus) mixed in with technical specs.
3. **Paraphrase Deduplication**: Datasets with duplicated and reworded compliance/pricing documents.
4. **Tool Schema Reduction**: Large API tool catalogs (10+ tools) reduced to only query-relevant schemas.
5. **Filler Phrase Compression**: Documents with heavy legal boilerplate and verbose padding.

---

## ⚖️ LLM Quality Judge (`backend/app/services/judge.py`)

To ensure that context optimization **does not degrade answer accuracy**, every run evaluates both the **Baseline Answer** and **Optimized Answer** using an LLM-as-a-Judge protocol.

### Scoring Rubric Output:
```json
{
  "score": 9.5,
  "rationale": "The answer accurately states all compliance standards required by the user.",
  "rubric_hits": [
    "Identifies PCI-DSS Level 1 compliance",
    "Confirms EU GDPR data residency support"
  ],
  "rubric_misses": []
}
```

---

## 📈 Benchmark Execution Command

To run the benchmark suite:
```bash
curl -X POST http://localhost:8000/api/v1/benchmarks/run \
     -H "Content-Type: application/json" \
     -d '{"task_ids": null}'
```

Or run pytest:
```bash
PYTHONPATH=backend python3 -m pytest backend/tests
```
