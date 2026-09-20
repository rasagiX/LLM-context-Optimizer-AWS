import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";

import { callModel } from "./ai-gateway.server";
import { buildContext, costOf, getTask, type Level } from "./benchmark/optimize";

const RunInput = z.object({
  taskId: z.string(),
  level: z.union([z.literal(0), z.literal(1), z.literal(2), z.literal(3)]),
});

export const runTask = createServerFn({ method: "POST" })
  .inputValidator((input: unknown) => RunInput.parse(input))
  .handler(async ({ data }) => {
    const task = getTask(data.taskId);
    const ctx = buildContext(task, data.level as Level);
    const result = await callModel(ctx.model, ctx.system, ctx.messages);

    return {
      taskId: task.id,
      level: data.level,
      model: ctx.model,
      answer: result.text,
      inputTokens: result.usage.inputTokens,
      outputTokens: result.usage.outputTokens,
      totalTokens: result.usage.inputTokens + result.usage.outputTokens,
      cost: costOf(ctx.model, result.usage.inputTokens, result.usage.outputTokens),
      ms: result.ms,
      includedDocs: ctx.includedDocs,
      includedTools: ctx.includedTools,
      historyMessages: ctx.historyMessages,
      approxContextTokens: ctx.approxTokens,
    };
  });

const JudgeInput = z.object({
  taskId: z.string(),
  baselineAnswer: z.string(),
  optimizedAnswer: z.string(),
});

const JUDGE_MODEL = "google/gemini-3.8-flash";

export const judgeTask = createServerFn({ method: "POST" })
  .inputValidator((input: unknown) => JudgeInput.parse(input))
  .handler(async ({ data }) => {
    const task = getTask(data.taskId);

    const prompt = `You are grading two AI answers to the same question against a reference answer. Grade only correctness and whether the requested output format was followed. Ignore verbosity differences and wording.

QUESTION:
${task.question}

REFERENCE ANSWER (ground truth):
${task.expected}

ANSWER A:
${data.baselineAnswer}

ANSWER B:
${data.optimizedAnswer}

Score each from 1 to 5 (5 = fully correct and correctly formatted, 1 = wrong). Reply with JSON only:
{"scoreA": number, "scoreB": number, "verdict": "A_better" | "B_better" | "tie", "note": "one short sentence"}`;

    const result = await callModel(JUDGE_MODEL, "You are a strict, terse grading judge. Reply with JSON only.", [
      { role: "user", content: prompt },
    ]);

    const match = result.text.match(/\{[\s\S]*\}/);
    let parsed = { scoreA: 0, scoreB: 0, verdict: "tie", note: result.text.slice(0, 160) };
    if (match) {
      try {
        parsed = { ...parsed, ...(JSON.parse(match[0]) as typeof parsed) };
      } catch {
        // keep fallback
      }
    }

    return {
      taskId: task.id,
      baselineScore: Number(parsed.scoreA) || 0,
      optimizedScore: Number(parsed.scoreB) || 0,
      verdict: parsed.verdict,
      note: parsed.note,
      judgeTokens: result.usage.inputTokens + result.usage.outputTokens,
    };
  });
