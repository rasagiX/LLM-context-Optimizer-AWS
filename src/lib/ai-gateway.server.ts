const GATEWAY = "https://ai.gateway.lovable.dev/v1";

export type Usage = { inputTokens: number; outputTokens: number };
export type ModelResult = { text: string; usage: Usage; ms: number; model: string };

type Msg = { role: "user" | "assistant"; content: string };

function key(): string {
  const k = process.env["LOVABLE_API_KEY"];
  if (!k) throw new Error("Missing LOVABLE_API_KEY");
  return k;
}

async function callResponses(model: string, system: string, messages: Msg[]): Promise<ModelResult> {
  const started = Date.now();
  const res = await fetch(`${GATEWAY}/responses`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Lovable-API-Key": key(),
      "X-Lovable-AIG-SDK": "fetch",
    },
    body: JSON.stringify({
      model,
      instructions: system,
      input: messages.map((m) => ({
        role: m.role,
        content: [{ type: m.role === "assistant" ? "output_text" : "input_text", text: m.content }],
      })),
      stream: true,
      store: false,
      reasoning: { effort: "low", summary: "auto" },
    }),
  });

  if (!res.ok || !res.body) {
    const detail = await res.text().catch(() => "");
    throw new Error(`AI gateway error ${res.status}: ${detail.slice(0, 400)}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let text = "";
  let reasoning = "";
  const usage: Usage = { inputTokens: 0, outputTokens: 0 };

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (!line.startsWith("data:")) continue;
      const payload = line.slice(5).trim();
      if (!payload || payload === "[DONE]") continue;
      let evt: Record<string, unknown>;
      try {
        evt = JSON.parse(payload);
      } catch {
        continue;
      }
      const type = evt["type"] as string | undefined;
      if (type === "response.output_text.delta") text += (evt["delta"] as string) ?? "";
      if (type === "response.reasoning_summary_text.delta") reasoning += (evt["delta"] as string) ?? "";
      if (type === "response.completed") {
        const response = evt["response"] as
          | { usage?: { input_tokens?: number; output_tokens?: number }; output_text?: string }
          | undefined;
        if (response?.usage) {
          usage.inputTokens = response.usage.input_tokens ?? 0;
          usage.outputTokens = response.usage.output_tokens ?? 0;
        }
        if (!text && response?.output_text) text = response.output_text;
      }
    }
  }

  return { text: text.trim() || reasoning.trim(), usage, ms: Date.now() - started, model };
}

async function callChat(model: string, system: string, messages: Msg[]): Promise<ModelResult> {
  const started = Date.now();
  const res = await fetch(`${GATEWAY}/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Lovable-API-Key": key(),
      "X-Lovable-AIG-SDK": "fetch",
    },
    body: JSON.stringify({
      model,
      messages: [{ role: "system", content: system }, ...messages],
    }),
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`AI gateway error ${res.status}: ${detail.slice(0, 400)}`);
  }

  const json = (await res.json()) as {
    choices?: { message?: { content?: string } }[];
    usage?: { prompt_tokens?: number; completion_tokens?: number };
  };

  return {
    text: (json.choices?.[0]?.message?.content ?? "").trim(),
    usage: {
      inputTokens: json.usage?.prompt_tokens ?? 0,
      outputTokens: json.usage?.completion_tokens ?? 0,
    },
    ms: Date.now() - started,
    model,
  };
}

export async function callModel(model: string, system: string, messages: Msg[]): Promise<ModelResult> {
  return model.startsWith("openai/")
    ? callResponses(model, system, messages)
    : callChat(model, system, messages);
}
