export type ModelId = "bedrock" | "gpt" | "claude" | "custom";
export type ContextKey = "history" | "documents" | "tools";

export type RunStats = {
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  cost: number;
  latency: number;
  prompt: string;
  answer: string;
};

export type Technique = {
  name: string;
  description: string;
  beforeTokens: number;
  afterTokens: number;
  savedPercent: number;
  enabled: boolean;
  icon: "prune" | "history" | "tools" | "dedupe";
};

export type OptimizeResponse = {
  original: RunStats;
  optimized: RunStats;
  savings: { tokenReduction: number; costReduction: number; latencyReduction: number };
  quality: {
    correctness: [number, number];
    completeness: [number, number];
    relevance: [number, number];
    consistency: [number, number];
    overall: [number, number];
    similarity: number;
    status: "preserved" | "rejected";
  };
  breakdown: Array<{ category: string; before: number; after: number }>;
  optimizations: Technique[];
};

export type BenchmarkTask = {
  id: string;
  type: string;
  before: number;
  after: number;
  saved: number;
  quality: number;
  status: "passed" | "running" | "queued";
};
