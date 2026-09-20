# AI Context Compiler — Backend

FastAPI backend for the **AI Context Compiler** — a middleware layer that reduces the number of tokens sent to an LLM on every call while preserving answer quality.

It runs a 5-step optimization pipeline on your inputs (question + conversation + documents + tools), calls the LLM before and after optimization in `compare` mode, then scores both answers through an LLM-as-judge to measure token savings vs. quality retention.

**LLM Provider:** Google Gemini (via `google-generativeai`)

---

## Features

- **5-step Context Compiler pipeline** — history compression, deduplication, context pruning, tool selection, prompt compression
- **Baseline vs. optimized comparison** — runs both pipelines and reports token/cost/latency reduction
- **LLM-as-judge quality scoring** — rubric-based evaluation (0–10) for every run
- **10-task benchmark suite** — fixed tasks across document QA, coding, tool use, multi-turn reasoning, data analysis, and more
- **DynamoDB-backed storage** — persistent run history when configured, in-memory fallback for local dev
- **Provider-independent LLM adapter** — swap models by changing one env var

---

## Quick Start

### 1. Clone and set up

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in:

```env
GEMINI_API_KEY=your_key_here
LLM_MODEL=gemini-1.5-flash
```

Get a free Gemini API key at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) — no billing required.

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive Swagger UI.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | ✅ Yes | — | Google Gemini API key |
| `LLM_MODEL` | No | `gemini-1.5-flash` | Model name (see options below) |
| `DYNAMODB_TABLE_NAME` | No | — | DynamoDB table for run storage. Leave blank for in-memory |
| `AWS_REGION` | No | `us-east-1` | AWS region (only needed if using DynamoDB) |
| `AWS_ACCESS_KEY_ID` | No | — | AWS credentials (only needed if using DynamoDB) |
| `AWS_SECRET_ACCESS_KEY` | No | — | AWS credentials (only needed if using DynamoDB) |
| `CORS_ORIGINS` | No | `*` | Comma-separated allowed origins. Tighten before deploying |

### Available models for `LLM_MODEL`

| Model | Speed | Quality | Cost |
|---|---|---|---|
| `gemini-1.5-flash` | ⚡ Fast | Good | Free tier |
| `gemini-1.5-pro` | Medium | Best | Paid |
| `gemini-2.0-flash` | ⚡ Fast | Great | Free tier |
| `gemini-2.0-flash-exp` | ⚡ Fast | Great | Free experimental |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `POST` | `/api/v1/run` | Run baseline and/or optimized pipeline |
| `GET` | `/api/v1/runs/{run_id}` | Fetch a previous run result |
| `POST` | `/api/v1/optimize` | Run the optimizer only (no LLM call) |
| `POST` | `/api/v1/evaluate` | Score an answer against a rubric |
| `POST` | `/api/v1/benchmarks/run` | Run the full benchmark suite |

### Run modes

`POST /api/v1/run` accepts a `mode` field:

| Mode | What it does |
|---|---|
| `compare` (default) | Runs both baseline and optimized, returns comparison stats |
| `baseline` | Runs full context through LLM only |
| `optimized` | Runs optimizer first, then LLM |

---

## Example Requests

### Compare baseline vs. optimized

```bash
curl -X POST http://localhost:8000/api/v1/run \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What was the revenue growth in Q3?",
    "documents": [
      {"id": "financials", "content": "Q2 revenue was $4,200,000. Q3 revenue was $5,100,000."}
    ],
    "rubric": ["Uses Q2 and Q3 revenue correctly", "Calculates percentage growth"],
    "mode": "compare"
  }'
```

### Optimizer only (no LLM call)

```bash
curl -X POST http://localhost:8000/api/v1/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the refund policy?",
    "documents": [
      {"id": "policy", "content": "Please note that our refund policy allows returns within 30 days."},
      {"id": "unrelated", "content": "Our office is located in New York."}
    ]
  }'
```

### Run benchmark suite

```bash
curl -X POST http://localhost:8000/api/v1/benchmarks/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

Run specific tasks only:

```bash
curl -X POST http://localhost:8000/api/v1/benchmarks/run \
  -H "Content-Type: application/json" \
  -d '{"task_ids": ["task_01", "task_03"]}'
```

---

## Project Structure

```
backend/
├── .env.example              Environment variable template
├── requirements.txt          Python dependencies
└── app/
    ├── main.py               FastAPI app entrypoint, CORS, health check
    ├── api/
    │   ├── routes.py         Aggregates all sub-routers under /api/v1
    │   ├── runs.py           POST /run, GET /runs/{id}
    │   ├── optimize.py       POST /optimize
    │   ├── evaluation.py     POST /evaluate
    │   └── benchmarks.py     POST /benchmarks/run
    ├── schemas/
    │   ├── requests.py       Pydantic input models
    │   └── responses.py      Pydantic output models
    ├── services/
    │   ├── llm.py            Google Gemini adapter (single LLM entry point)
    │   ├── judge.py          LLM-as-judge rubric scoring
    │   └── store.py          Run storage — DynamoDB or in-memory fallback
    ├── optimizer/            The Context Compiler pipeline
    │   ├── pipeline.py       Orchestrates all 5 steps
    │   ├── history_compressor.py  LLM-based conversation summarization
    │   ├── deduplicator.py   Exact + near-duplicate document removal
    │   ├── context_pruner.py TF-IDF cosine relevance filtering
    │   ├── tool_selector.py  TF-IDF cosine tool ranking (top-N)
    │   ├── prompt_compressor.py   5-pass filler/whitespace removal
    │   └── token_utils.py    tiktoken-based token counting
    └── benchmark/
        ├── tasks.json        10 fixed benchmark tasks
        ├── runner.py         Executes tasks through the run pipeline
        └── metrics.py        Aggregates token reduction + quality scores
```

---

## The Optimizer Pipeline

The 5 steps run in sequence on every optimized call:

| Step | What it does |
|---|---|
| **History Compressor** | Summarises conversation turns older than the last 6 using an LLM call. Falls back to a heuristic if the LLM call fails |
| **Deduplicator** | Removes exact-duplicate documents (SHA-256) and near-duplicates (Jaccard shingle similarity, threshold 0.85) |
| **Context Pruner** | Scores each document by TF-IDF cosine similarity with the question. Drops documents below the relevance threshold |
| **Tool Selector** | Same TF-IDF scoring — keeps only the top-5 most relevant tools |
| **Prompt Compressor** | 5-pass regex compressor: strips filler phrases, redundant preambles, verbose list intros, excess whitespace, and duplicate sentences |

---

## Benchmark Tasks

10 fixed tasks across 6 categories:

| ID | Category | What it tests |
|---|---|---|
| `task_01` | document_qa | Revenue growth calculation from a financial doc |
| `task_02` | long_conversation | Region decision from a 12-turn conversation |
| `task_03` | coding | Palindrome function implementation |
| `task_04` | tool_using_agent | Weather tool selection from 5 available tools |
| `task_05` | multi_document_qa | Lowest-cost vendor across 3 vendor docs + 1 irrelevant doc |
| `task_06` | multi_turn_reasoning | Architecture recommendation from constraints conversation |
| `task_07` | data_analysis | Highest profit margin product from sales data |
| `task_08` | customer_support | Late order resolution using shipping policy doc |
| `task_09` | multi_tool_workflow | 3-tool workflow: stock price + calendar + email |
| `task_10` | complex_reasoning | Monolith vs. microservices decision from 4 docs |

---

## Response Shape (compare mode)

```json
{
  "run_id": "run_abc123",
  "baseline": {
    "input_tokens": 312,
    "output_tokens": 87,
    "total_tokens": 399,
    "latency_ms": 1240,
    "cost": 0.000034,
    "answer": "..."
  },
  "optimized": {
    "input_tokens": 198,
    "output_tokens": 85,
    "total_tokens": 283,
    "latency_ms": 980,
    "cost": 0.000022,
    "answer": "..."
  },
  "comparison": {
    "token_reduction_percent": 36.5,
    "cost_reduction_percent": 35.3,
    "latency_reduction_percent": 21.0,
    "quality_baseline": 8.5,
    "quality_optimized": 8.0
  }
}
```

