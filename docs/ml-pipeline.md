# ML & NLP Pipeline Documentation

The `ml/` package provides vector embedding, semantic similarity scoring, near-duplicate detection, text chunking, and token reduction statistics for the **AI Context Compiler**.

---

## 🔬 Core Components & Algorithms

### 1. Vector Embedder (`ml/embedder.py`)
Supported Backends:
- **`local` (Default)**: `sentence-transformers/all-MiniLM-L6-v2`
  - 384-dimensional dense vectors
  - Runs locally on CPU, no network egress or AWS key needed
- **`bedrock`**: `Amazon Titan Embeddings V2` (`amazon.titan-embed-text-v2:0`)
  - 512-dimensional unit-normalized vectors
  - High accuracy for multi-lingual and technical contexts

### 2. Semantic Similarity Scorer (`ml/scorer.py`)
Computes cosine similarity between query vector $q \in \mathbb{R}^d$ and document vector $d_i \in \mathbb{R}^d$:

$$\text{CosineSimilarity}(q, d_i) = \frac{q \cdot d_i}{\|q\| \|d_i\|}$$

- Matrix multiplication (`chunk_units @ query_unit`) provides sub-millisecond vectorized scoring across hundreds of documents.
- Documents scoring below `RELEVANCE_THRESHOLD` (default: 0.2) are pruned.

### 3. Greedy Near-Duplicate Detector (`ml/deduplicator.py`)
Compares document embeddings against already-retained documents:
- If $\max_{j \in \text{retained}} \text{CosineSimilarity}(d_i, d_j) \ge \text{threshold}$ (default: 0.85), document $d_i$ is flagged as a near-duplicate and dropped.
- Catches paraphrases and rewordings that exact SHA-256 hashing misses.

### 4. Text Chunking Strategies (`ml/chunker.py`)
- `sentence`: Splitting on sentence boundaries (`.`, `!`, `?`).
- `paragraph`: Splitting on double newline boundaries.
- `fixed`: Fixed-window word chunking with configurable overlap.

### 5. Token Counting & Statistics (`ml/utils.py`)
- Accurate token counting via `tiktoken` (`cl100k_base`).
- Calculates original tokens, retained tokens, tokens saved, and percentage reduction.
