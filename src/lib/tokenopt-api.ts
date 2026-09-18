import type { BenchmarkTask, ContextKey, ModelId, OptimizeResponse } from "./tokenopt-types";

export const API_ENDPOINTS = {
  optimize: "/api/optimize",
  evaluate: "/api/evaluate",
  benchmark: "/api/benchmark",
  analytics: "/api/analytics",
  costEstimate: "/api/cost-estimate",
} as const;

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const originalPrompt = `SYSTEM:\nYou are a highly capable AI assistant. Provide accurate, complete and useful answers. Follow all prior policies and instructions.\n\nCONVERSATION HISTORY:\nUser: I am building a browser-based video calling application.\nAssistant: I can help with the application architecture.\nUser: It should support peer-to-peer calling and reconnect gracefully.\nAssistant: We should consider signaling, ICE, STUN and TURN.\n[... 34 earlier messages ...]\n\nDOCUMENTS:\nWebRTC architecture guide (full document)\nBrowser media APIs (full document)\nDeployment handbook (full document)\n\nTOOLS:\nsearch_document(), read_file(), write_file(), fetch_url(), query_database(), send_email(), create_ticket(), analyze_image() [... 12 more]\n\nUSER:\nExplain how WebRTC works and how signaling is used in a video calling application.`;

const optimizedPrompt = `SYSTEM:\nAnswer accurately and explain concepts clearly.\n\nRELEVANT HISTORY:\nUser is building a browser video calling application with resilient peer-to-peer connections.\n\nRELEVANT DOCUMENT:\nWebRTC architecture: peer connections, ICE negotiation, STUN/TURN, and signaling.\n\nREQUIRED TOOL:\nsearch_document()\n\nUSER:\nExplain how WebRTC works and how signaling is used in a video calling application.`;

const originalAnswer = `WebRTC enables real-time audio, video, and data exchange directly between browsers. A call begins when each client captures media, creates an RTCPeerConnection, and generates an SDP offer or answer describing its media capabilities. ICE then gathers possible network paths, while STUN discovers public addresses and TURN relays traffic when a direct route cannot be established.\n\nSignaling is the coordination channel used before the peer-to-peer media path exists. Your application sends SDP offers, answers, and ICE candidates through a WebSocket or similar server. The signaling server does not usually carry the call media; it only introduces peers and exchanges connection metadata. After negotiation succeeds, encrypted media flows directly between peers or through TURN when necessary.`;

const optimizedAnswer = `WebRTC creates an encrypted, real-time connection for audio, video, or data between browsers. Each client creates an RTCPeerConnection, describes its media capabilities in an SDP offer or answer, and uses ICE to test network routes. STUN helps discover public network addresses; TURN provides a relay when a direct connection is blocked.\n\nSignaling is the setup channel. Your app uses a WebSocket or similar server to exchange SDP offers, answers, and ICE candidates between participants. The signaling server coordinates the connection but normally does not carry the media itself. Once negotiation completes, media travels peer-to-peer or through TURN as a fallback.`;

export const MOCK_OPTIMIZATION: OptimizeResponse = {
  original: { inputTokens: 18420, outputTokens: 850, totalTokens: 19270, cost: 0.00405, latency: 4.8, prompt: originalPrompt, answer: originalAnswer },
  optimized: { inputTokens: 5420, outputTokens: 830, totalTokens: 6250, cost: 0.00128, latency: 2.3, prompt: optimizedPrompt, answer: optimizedAnswer },
  savings: { tokenReduction: 70.6, costReduction: 68.4, latencyReduction: 41.2 },
  quality: { correctness: [96, 96], completeness: [94, 93], relevance: [97, 97], consistency: [95, 96], overall: [95.2, 95.5], similarity: 96.8, status: "preserved" },
  breakdown: [
    { category: "System instructions", before: 2000, after: 700 },
    { category: "Conversation history", before: 6000, after: 700 },
    { category: "Documents", before: 4000, after: 1200 },
    { category: "Tool schemas", before: 2000, after: 300 },
    { category: "User query", before: 420, after: 420 },
  ],
  optimizations: [
    { name: "Context Pruning", icon: "prune", beforeTokens: 6000, afterTokens: 1200, savedPercent: 80, enabled: true, description: "Removed conversation and document content unrelated to the question." },
    { name: "History Summarization", icon: "history", beforeTokens: 4000, afterTokens: 700, savedPercent: 82.5, enabled: true, description: "Condensed long history into a summary containing only useful details." },
    { name: "Tool Schema Trimming", icon: "tools", beforeTokens: 2000, afterTokens: 300, savedPercent: 85, enabled: true, description: "Included only the tools required for this request." },
    { name: "Prompt Deduplication", icon: "dedupe", beforeTokens: 1000, afterTokens: 250, savedPercent: 75, enabled: true, description: "Removed repeated instructions and boilerplate." },
  ],
};

export async function optimizeRequest(input: { question: string; model: ModelId; context: ContextKey[] }) {
  await delay(300);
  return { ...MOCK_OPTIMIZATION, request: input };
}
export async function evaluateRequest() { await delay(250); return MOCK_OPTIMIZATION.quality; }

export const BENCHMARK_TASKS: BenchmarkTask[] = [
  { id: "T01", type: "Factual", before: 12450, after: 4120, saved: 66.9, quality: 95, status: "passed" },
  { id: "T02", type: "Coding", before: 18200, after: 7320, saved: 59.8, quality: 94, status: "passed" },
  { id: "T03", type: "Document QA", before: 9800, after: 3900, saved: 60.2, quality: 96, status: "passed" },
  { id: "T04", type: "Tool Use", before: 25840, after: 9725, saved: 62.4, quality: 95, status: "passed" },
  { id: "T05", type: "Summarization", before: 15320, after: 5210, saved: 66, quality: 94, status: "passed" },
  { id: "T06", type: "Multi-turn", before: 22100, after: 7950, saved: 64, quality: 95, status: "passed" },
  { id: "T07", type: "Extraction", before: 11880, after: 4890, saved: 58.8, quality: 97, status: "passed" },
  { id: "T08", type: "Planning", before: 17400, after: 6630, saved: 61.9, quality: 93, status: "passed" },
  { id: "T09", type: "Analysis", before: 20100, after: 7520, saved: 62.6, quality: 94, status: "passed" },
  { id: "T10", type: "Structured output", before: 13600, after: 5020, saved: 63.1, quality: 95, status: "passed" },
];
export async function runBenchmark() { await delay(500); return BENCHMARK_TASKS; }

export const MODEL_PRICING: Record<ModelId, { label: string; inputPerMillion: number; outputPerMillion: number }> = {
  bedrock: { label: "Amazon Bedrock", inputPerMillion: 3, outputPerMillion: 15 },
  gpt: { label: "GPT", inputPerMillion: 2.5, outputPerMillion: 10 },
  claude: { label: "Claude", inputPerMillion: 3, outputPerMillion: 15 },
  custom: { label: "Custom Model", inputPerMillion: 2, outputPerMillion: 8 },
};
export function estimateCost(input: { requests: number; inputTokens: number; outputTokens: number; model: ModelId }) {
  const price = MODEL_PRICING[input.model];
  const beforeTokens = input.requests * (input.inputTokens + input.outputTokens);
  const afterInput = input.inputTokens * 0.376;
  const afterTokens = input.requests * (afterInput + input.outputTokens * 0.976);
  const beforeCost = input.requests * ((input.inputTokens / 1e6) * price.inputPerMillion + (input.outputTokens / 1e6) * price.outputPerMillion);
  const afterCost = input.requests * ((afterInput / 1e6) * price.inputPerMillion + ((input.outputTokens * 0.976) / 1e6) * price.outputPerMillion);
  return { beforeTokens, afterTokens, beforeCost, afterCost, monthlySavings: beforeCost - afterCost };
}
