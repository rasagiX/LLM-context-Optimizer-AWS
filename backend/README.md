# AI Context Compiler — Backend

FastAPI backend for the AI Context Compiler. Runs a task through a baseline
pipeline (full context) and an optimized pipeline (pruned/compressed
context), then scores both answers with an LLM-based quality judge so you
can measure token/cost/latency savings against a quality threshold.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # fill in AWS credentials + region
```

AWS credentials need `bedrock:InvokeModel` permission, and the model in
`BEDROCK_MODEL_ID` must be enabled in your Bedrock console for that region.

## Run

```bash
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API docs.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/api/v1/run` | Run a task through baseline and/or optimized pipeline |
| POST | `/api/v1/optimize` | Run just the Context Compiler (no LLM call) |
| POST | `/api/v1/evaluate` | Score an answer against a rubric |
| GET | `/api/v1/runs/{run_id}` | Fetch a previous run |
| POST | `/api/v1/benchmarks/run` | Run the fixed benchmark suite (`app/benchmark/tasks.json`) |

## Quick test

```bash
curl -X POST http://localhost:8000/api/v1/run \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What was the revenue growth in Q3?",
    "documents": [{"id": "d1", "content": "Q2 revenue was $4,200,000. Q3 revenue was $5,100,000."}],
    "rubric": ["Uses Q2 and Q3 revenue correctly", "Calculates percentage growth"],
    "mode": "compare"
  }'
```

Run the full fixed benchmark:

```bash
curl -X POST http://localhost:8000/api/v1/benchmarks/run -H "Content-Type: application/json" -d '{}'
```

## Project layout

```
app/
├── main.py                  FastAPI app + /health
├── api/                     Route handlers (thin — logic lives in services/optimizer)
│   ├── routes.py            Aggregates sub-routers
│   ├── runs.py               /run, /runs/{id}
│   ├── optimize.py           /optimize
│   ├── evaluation.py         /evaluate
│   └── benchmarks.py         /benchmarks/run
├── schemas/                 Pydantic request/response models
├── services/
│   ├── bedrock.py           Bedrock invoke_model wrapper — the only place boto3 is called
│   ├── judge.py             LLM-as-judge rubric scoring
│   └── store.py             Run storage (in-memory; swap for DynamoDB later)
├── optimizer/                The Context Compiler
│   ├── pipeline.py           Orchestrates the steps below
│   ├── context_pruner.py     Keyword-overlap relevance filtering
│   ├── tool_selector.py      Keeps top-N relevant tools
│   ├── history_compressor.py Collapses old turns into a summary
│   ├── deduplicator.py       Exact-match content dedup
│   ├── prompt_compressor.py  Strips filler phrases / whitespace
│   └── token_utils.py        tiktoken-based (or heuristic) token counting
└── benchmark/
    ├── tasks.json             Fixed 5-task benchmark suite (extend to ~10)
    ├── runner.py              Runs tasks.json through the /run logic
    └── metrics.py             Aggregates results across tasks
```

## Status vs. the build plan

Done: Steps 1–4 (FastAPI, LLM connection, baseline runner, first optimizer
pass) plus a working quality judge and benchmark runner (Steps 5–8, in a
simple form).

Still placeholder / TODO, called out in the relevant files:
- **Optimizer heuristics** (`context_pruner.py`, `tool_selector.py`,
  `history_compressor.py`, `deduplicator.py`) use keyword overlap / exact
  match as a cheap v0. Swap for embeddings or an LLM pass once you've
  benchmarked whether it's worth the added cost/latency.
- **Cost** is hardcoded to `0.0` in `runs.py` — needs a per-model pricing
  table (ties into Step 6, model routing).
- **Storage** (`services/store.py`) is in-memory — swap for DynamoDB before
  deploying (Step 10).
- **Benchmark suite** has 5 of the ~10 tasks the spec calls for — the
  remaining categories (multi-turn reasoning, data analysis, customer
  support, multi-tool workflow, complex reasoning) still need tasks added
  to `tasks.json`.
