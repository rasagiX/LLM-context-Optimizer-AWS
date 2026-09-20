# Advanced ML & NLP Pipeline Documentation — AI Context Compiler

The `ml/` package provides high-performance vector embedding, semantic similarity scoring, two-stage cross-encoder reranking, LLMLingua-style Query Mutual Information token compression, tool schema minification, vector tool routing, near-duplicate detection, and semantic preservation metrics for the **AI Context Compiler**.

---

## 🔬 Core Components & Algorithms

### 1. Multi-Backend Vector Embedder (`ml/embedder.py`)
Supported Backends:
- **`local` (Default)**: `sentence-transformers/all-MiniLM-L6-v2`
  - 384-dimensional dense vectors
  - Runs locally on CPU, zero network latency or API key required
- **`bedrock`**: `Amazon Titan Embeddings V2` (`amazon.titan-embed-text-v2:0`)
  - 512-dimensional unit-normalized vectors
  - Executed concurrently via multi-threaded `ThreadPoolExecutor` for high throughput

### 2. Semantic Similarity Scorer (`ml/scorer.py`)
Computes cosine similarity between query vector $q \in \mathbb{R}^d$ and document vector $d_i \in \mathbb{R}^d$:

$$\text{CosineSimilarity}(q, d_i) = \frac{q \cdot d_i}{\|q\| \|d_i\|}$$

- Vectorized matrix multiplication (`chunk_units @ query_unit`) provides sub-millisecond scoring across hundreds of candidate documents.

### 3. Two-Stage Retrieval & Reranker (`ml/reranker.py`)
- **Stage 1 (Bi-Encoder Filter)**: Fast vector cosine similarity filtering to isolate top $M$ candidate passages.
- **Stage 2 (Cross-Encoder Reranker)**: Joint cross-attention scoring (`cross-encoder/ms-marco-MiniLM-L-6-v2`) over (query, document) pairs for fine-grained ranking precision before final thresholding.

### 4. Query Mutual Information Token Compressor (`ml/token_compressor.py`)
- Computes token-level mutual information $I(w; Q) = \cos(\vec{v}_w, \vec{v}_Q) \cdot \text{IDF}(w)$ (LLMLingua-style).
- Simplifies padded prepositions ("in order to" -> "to") and removes low-information modifiers.
- Strictly protects numbers, technical terms, and compliance standards (e.g. PCI-DSS, GDPR, SOC 2, HIPAA, AWS).

### 5. Tool & Schema Signature Minifier (`ml/schema_minifier.py`)
- Converts verbose 30-line JSON tool schemas into compact TypeScript-style inline function signatures or compact JSON strings.
- Example: `get_compliance_report(provider: string, region?: string): Fetch compliance report`
- Saves **80% - 85% of input tokens** consumed by tool catalogs!

### 6. Semantic Vector Tool Selector (`app/optimizer/tool_selector.py`)
- Uses vector embedding similarity between user queries and tool definitions (name + description).
- Enables natural language tool schema filtering (e.g. mapping "credit card compliance" to `get_compliance_report`).

### 7. Vector Boundary Semantic Topic Chunker (`ml/chunker.py`)
- Calculates cosine distance between consecutive sentence embeddings to place chunk split points ONLY at topic shift boundaries.

### 8. Greedy Near-Duplicate Detector (`ml/deduplicator.py`)
- Compares document embeddings against already-retained documents:
- If $\max_{j \in \text{retained}} \text{CosineSimilarity}(d_i, d_j) \ge \text{threshold}$ (default: 0.85), document $d_i$ is flagged as a near-duplicate and dropped.

### 9. ML Quality & Semantic Preservation Evaluator (`ml/evaluator.py`)
- Measures vector cosine similarity between raw context embedding and optimized context embedding to yield the **Semantic Preservation Score** ($0.0 - 1.0$).
- Emits `SemanticPreservationScore` custom metrics directly to AWS CloudWatch.

---

## 🚀 Interactive Demonstration

Run the comprehensive ML pipeline demo script:
```bash
PYTHONPATH=backend:. /opt/anaconda3/bin/python3 demo.py
```
