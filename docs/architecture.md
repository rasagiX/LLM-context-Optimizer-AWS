# Architecture Overview - AI Context Compiler

The **AI Context Compiler** is an enterprise-grade middleware component designed to sit between client applications and Large Language Models (LLMs) like Amazon Bedrock (Claude 3.5 Sonnet). Its primary purpose is to drastically reduce input token consumption while preserving answer accuracy and semantic fidelity.

---

## 🏗️ High-Level System Architecture

```
                    Client Application / Frontend
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

## 📦 Core Components

### 1. FastAPI API Layer (`backend/app/api/`)
- `routes.py`: Aggregates `/api/v1` routes.
- `optimize.py`: Exposes `/optimize` and `/optimize/demo` for fast, zero-LLM-cost token compression.
- `runs.py`: Exposes `/run` to execute baseline and optimized context against Amazon Bedrock.
- `evaluation.py`: Exposes `/evaluate` for scoring answers via the LLM Quality Judge.
- `benchmarks.py`: Exposes `/benchmarks/run` to execute fixed test suites.

### 2. 5-Step Optimizer Pipeline (`backend/app/optimizer/`)
- `history_compressor.py`: Compresses history beyond 6 turns into a structured system summary.
- `deduplicator.py`: Uses SHA-256 exact hashing followed by greedy embedding-based near-duplicate detection.
- `context_pruner.py`: Calculates sentence-transformer or Titan embedding cosine similarity between question and documents.
- `tool_selector.py`: Filters tool schema definitions down to the top-N relevant tools.
- `prompt_compressor.py`: Strips verbose filler phrases ("please note that", "as mentioned above") and normalizes whitespace.

### 3. ML Package (`ml/`)
- `embedder.py`: Dual-backend vector generation (`local` MiniLM vs `bedrock` Titan V2).
- `scorer.py`: Vectorized matrix multiplication for cosine similarity.
- `pruner.py`: High-level context pruning orchestration.
- `deduplicator.py`: Pairwise similarity matrix deduplication.
- `chunker.py`: Sentence, paragraph, and fixed-window text segmentation.
- `utils.py`: Tiktoken token counting and reduction statistics.

### 4. AWS Services (`backend/app/services/`)
- `bedrock.py`: Boto3 Bedrock Converse API integration with local mock fallback.
- `judge.py`: LLM-as-a-Judge rubric evaluator.
- `s3.py`: Json artifact persistence to S3 buckets.
- `cloudwatch.py`: Custom metric emission (`TokensSaved`, `OptimizationLatency`, `TokenReductionPercent`).
- `config.py`: Centralized configuration settings.
