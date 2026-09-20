import {
  BOILERPLATE,
  COMPACT_SYSTEM,
  DOCS,
  HISTORY,
  HISTORY_SUMMARY,
  TASKS,
  TOOLS,
  VERBOSE_SYSTEM,
  type Task,
  type ToolSchema,
} from "./workload";

export type Level = 0 | 1 | 2 | 3;

export const LEVELS: { level: Level; name: string; techniques: string[] }[] = [
  {
    level: 0,
    name: "Naive baseline",
    techniques: [
      "Full 1,000-word system prompt",
      "All 30 tool schemas",
      "All 6 documents attached",
      "Full 10-message history verbatim",
      "Boilerplate pasted twice",
      "Everything on the large model",
    ],
  },
  {
    level: 1,
    name: "Compress + dedup",
    techniques: ["Compressed system prompt", "Boilerplate deduplicated to one copy"],
  },
  {
    level: 2,
    name: "+ prune context & tools",
    techniques: ["Only relevant documents attached", "Only relevant tool schemas (max 4)"],
  },
  {
    level: 3,
    name: "+ summarize & route",
    techniques: ["History replaced by a one-line summary", "Easy non-numeric tasks routed to the small model"],
  },
];

export const LARGE_MODEL = "openai/gpt-6-astra";
export const SMALL_MODEL = "google/gemini-3.1-flash-lite";

export type Message = { role: "user" | "assistant"; content: string };

export type BuiltContext = {
  system: string;
  messages: Message[];
  model: string;
  includedDocs: string[];
  includedTools: string[];
  historyMessages: number;
  approxTokens: number;
};

export function approxTokens(text: string): number {
  return Math.ceil(text.length / 4);
}

function score(tags: string[], task: Task): number {
  const haystack = `${task.question} ${task.title} ${task.tags.join(" ")}`.toLowerCase();
  let hits = 0;
  for (const tag of tags) if (haystack.includes(tag.toLowerCase())) hits += 1;
  for (const tag of task.tags) if (tags.some((t) => t.toLowerCase() === tag.toLowerCase())) hits += 2;
  return hits;
}

function renderTools(tools: ToolSchema[]): string {
  if (tools.length === 0) return "";
  return `Available tools:\n${tools
    .map((t) => `- ${t.name}(${t.parameters}): ${t.description}`)
    .join("\n")}`;
}

function renderToolsCompact(tools: ToolSchema[]): string {
  if (tools.length === 0) return "";
  return `Tools: ${tools.map((t) => `${t.name}(${t.parameters})`).join(", ")}`;
}

export function buildContext(task: Task, level: Level): BuiltContext {
  const compress = level >= 1;
  const prune = level >= 2;
  const summarize = level >= 3;
  const route = level >= 3;

  const docs = prune
    ? DOCS.map((d) => ({ d, s: score(d.tags, task) }))
        .filter((x) => x.s > 0)
        .sort((a, b) => b.s - a.s)
        .slice(0, 2)
        .map((x) => x.d)
    : DOCS;

  const tools = prune
    ? TOOLS.map((t) => ({ t, s: score(t.tags, task) }))
        .filter((x) => x.s > 0)
        .sort((a, b) => b.s - a.s)
        .slice(0, 4)
        .map((x) => x.t)
    : TOOLS;

  const systemParts: string[] = [];
  systemParts.push(compress ? COMPACT_SYSTEM : VERBOSE_SYSTEM);
  systemParts.push(BOILERPLATE);
  if (!compress) systemParts.push(BOILERPLATE); // duplicated boilerplate in the naive version
  systemParts.push(prune ? renderToolsCompact(tools) : renderTools(tools));

  const system = systemParts.filter(Boolean).join("\n\n");

  const docBlock = docs
    .map((d) => `### ${d.title}\n${d.text}`)
    .join("\n\n");

  const messages: Message[] = [];
  if (summarize) {
    messages.push({ role: "user", content: HISTORY_SUMMARY });
    messages.push({ role: "assistant", content: "Understood." });
  } else {
    messages.push(...HISTORY);
  }
  messages.push({
    role: "user",
    content: docBlock
      ? `Reference documents:\n\n${docBlock}\n\nQuestion: ${task.question}`
      : `Question: ${task.question}`,
  });

  // Difficulty router: cheap model only for easy tasks that are not numeric/precision work,
  // where a small model reliably matches the large one.
  const routable = task.difficulty === "easy" && !task.tags.includes("math");
  const model = route && routable ? SMALL_MODEL : LARGE_MODEL;

  return {
    system,
    messages,
    model,
    includedDocs: docs.map((d) => d.title),
    includedTools: tools.map((t) => t.name),
    historyMessages: summarize ? 2 : HISTORY.length,
    approxTokens: approxTokens(system + messages.map((m) => m.content).join("")),
  };
}

export function getTask(id: string): Task {
  const task = TASKS.find((t) => t.id === id);
  if (!task) throw new Error(`Unknown task: ${id}`);
  return task;
}

export const PRICING: Record<string, { input: number; output: number }> = {
  [LARGE_MODEL]: { input: 0.00001, output: 0.00005 },
  [SMALL_MODEL]: { input: 0.00000025, output: 0.0000015 },
  "google/gemini-3.8-flash": { input: 0.00000075, output: 0.00000375 },
};

export function costOf(model: string, inputTokens: number, outputTokens: number): number {
  const p = PRICING[model] ?? { input: 0, output: 0 };
  return inputTokens * p.input + outputTokens * p.output;
}
