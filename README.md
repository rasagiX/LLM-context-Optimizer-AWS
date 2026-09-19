# AI Context Compiler (LLM Context Optimizer - AWS)

> Enterprise middleware that reduces LLM input token consumption by 40%–70% while maintaining answer quality, reducing latency, and lowering AWS Bedrock inference costs.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![AWS Bedrock](https://img.shields.io/badge/AWS_Bedrock-Claude_3.5_Sonnet-FF9900.svg?style=flat&logo=amazon-aws)](https://aws.amazon.com/bedrock/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python)](https://python.org)
[![Pytest](https://img.shields.io/badge/Tests-Passing-brightgreen.svg?style=flat&logo=pytest)](https://pytest.org)

---

## 🚀 Key Features

- ⚡ **5-Step ML Optimizer Pipeline**:
  1. **History Compressor**: Collapses turns older than 6 turns into structured summaries.
  2. **Deduplicator**: Exact SHA-256 hash dedup + MiniLM/Titan cosine near-duplicate removal.
  3. **Context Pruner**: Semantic cosine similarity pruning against the query.
  4. **Tool Selector**: Drops zero-overlap/irrelevant tool schemas from the system prompt.
  5. **Prompt Compressor**: Strips 20+ filler phrase patterns & normalizes whitespace.
- ☁️ **AWS Bedrock Integration**: Bedrock Converse API for Claude 3.5 Sonnet / Haiku and Amazon Titan Embeddings V2.
- 🛠️ **Zero-Credential Local Mock Mode (`AWS_ENABLED=false`)**: Full support for running and testing locally without an AWS account.
- 📊 **LLM Quality Judge**: Automated rubric evaluation comparing baseline vs. optimized answer quality.
- 📈 **AWS CloudWatch & S3 Persistence**: Emits custom metrics (`TokensSaved`, `OptimizationLatency`, `TokenReductionPercent`) and saves run histories to S3.
- 💻 **Interactive UI Dashboard**: React + Vite + TanStack frontend for real-time optimization, benchmarking, and analytics.

---

## 🏛️ System Architecture

```
                    Client Application / Frontend UI
                                 │
                                 ▼
                     FastAPI REST Gateway
                                 │
         ┌───────────────────────┴───────────────────────┐
         ▼                                               ▼
POST /api/v1/optimize                             POST /api/v1/run
(Token Reduction Only - Local)                 (Baseline vs Optimized LLM Run)
         │                                               │
         ▼                                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      5-Step Optimizer Pipeline                         │
│                                                                        │
│  1. History Compressor ──► Summarizes old conversation turns (>6)      │
│  2. Deduplicator       ──► Exact SHA-256 + Embedding near-dup filter  │
│  3. Context Pruner     ──► Vector cosine similarity filtering          │
│  4. Tool Selector      ──► Drops zero-overlap/irrelevant tool schemas  │
│  5. Prompt Compressor  ──► Strips 20+ filler phrases & whitespace      │
└────────────────────────────────────────────────────────────────────────┘
         │                                               │
         ▼                                               ▼
Returns Optimized Context                       Amazon Bedrock (Converse API)
+ % Tokens Saved                                ├── Baseline Claude Call
+ Metrics                                       ├── Optimized Claude Call
                                                └── LLM Quality Judge Scoring
                                                         │
                                                         ▼
                                                AWS S3 & CloudWatch Metrics
```

---

## ⚡ Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/rasagiX/LLM-context-Optimizer-AWS.git
cd LLM-context-Optimizer-AWS

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Environment Setup

Copy `.env.example` to `.env` in `backend/`:

```bash
cp backend/.env.example backend/.env
```

To run in **Local Mock Mode** (no AWS credentials required):
```env
AWS_ENABLED=false
EMBEDDER_BACKEND=local
```

To run with **AWS Bedrock**:
```env
AWS_ENABLED=true
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
EMBEDDER_BACKEND=local
```

### 3. Start Server

```bash
# Start FastAPI server
PYTHONPATH=backend uvicorn app.main:app --reload --port 8000
```

FastAPI interactive docs will be available at: `http://localhost:8000/docs`

---

## 🧪 Quick Test / Smoke Test

Run the zero-argument demo endpoint to verify all 5 optimizer steps:

```bash
curl http://localhost:8000/api/v1/optimize/demo
```

Sample JSON Output:
```json
{
  "original_tokens": 1240,
  "optimized_tokens": 580,
  "reduction_percent": 53.23,
  "tokens_saved": 660,
  "optimization_latency_ms": 12,
  "cost_saved_est": 0.00198,
  "steps_applied": [
    "history_compressor",
    "deduplicator",
    "context_pruner",
    "tool_selector",
    "prompt_compressor"
  ]
}
```

---

## 🧪 Running Pytest Test Suite

Run unit and integration tests:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests
```

---

## 📖 Documentation Links

Detailed technical documentation is available in the [`docs/`](file:///Users/manasapoosa/LLM-context-Optimizer-AWS/docs) directory:
- 🏗️ [Architecture Overview](docs/architecture.md)
- ⚙️ [AWS Setup & IAM Guide](docs/aws-setup.md)
- 🔬 [ML Pipeline & Vector Embeddings](docs/ml-pipeline.md)
- 📊 [Benchmark & Evaluation Suite](docs/evaluation.md)

---

## 📜 License

MIT License.
