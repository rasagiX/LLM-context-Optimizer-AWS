import { useEffect, useRef, useState } from "react";
import { AreaChart, BarChart3, BookOpen, Braces, Check, CheckCircle2, ChevronDown, CircleDollarSign, Clock3, Copy, Files, Gauge, History, Layers3, LoaderCircle, Scissors, ShieldCheck, Sparkles, Target, WandSparkles, Wrench, Zap } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { PageIntro } from "./app-shell";
import { MetricCard, SectionHeading, StatusPill } from "./shared";
import { MOCK_OPTIMIZATION, optimizeRequest } from "@/lib/tokenopt-api";
import type { ContextKey, ModelId, OptimizeResponse, Technique } from "@/lib/tokenopt-types";
import { cn } from "@/lib/utils";

const EXAMPLE = "Explain how WebRTC works and how signaling is used in a video calling application.";
const steps = ["Parsing request", "Counting original tokens", "Finding relevant context", "Removing duplicate instructions", "Selecting required tools", "Compressing conversation history", "Generating optimized prompt", "Running quality check"];
const contextOptions: Array<{ id: ContextKey; label: string; icon: typeof History }> = [{ id: "history", label: "Conversation History", icon: History }, { id: "documents", label: "Documents", icon: Files }, { id: "tools", label: "Tool Definitions", icon: Wrench }];
const techniqueIcons = { prune: Scissors, history: History, tools: Wrench, dedupe: Layers3 };

export function OptimizeDashboard() {
  const [question, setQuestion] = useState("");
  const [model, setModel] = useState<ModelId>("bedrock");
  const [context, setContext] = useState<ContextKey[]>(["history", "documents", "tools"]);
  const [stage, setStage] = useState<"input" | "analyzing" | "results">("input");
  const [step, setStep] = useState(0);
  const [result, setResult] = useState<OptimizeResponse>(MOCK_OPTIMIZATION);
  const [techniques, setTechniques] = useState<Technique[]>(MOCK_OPTIMIZATION.optimizations);
  const [copied, setCopied] = useState(false);
  const resultsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (stage !== "analyzing") return;
    if (step < steps.length) { const timer = window.setTimeout(() => setStep((v) => v + 1), 260); return () => window.clearTimeout(timer); }
    const timer = window.setTimeout(() => { setStage("results"); requestAnimationFrame(() => resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })); }, 300);
    return () => window.clearTimeout(timer);
  }, [stage, step]);

  async function analyze() {
    if (!question.trim()) setQuestion(EXAMPLE);
    setStage("analyzing"); setStep(0);
    const response = await optimizeRequest({ question: question.trim() || EXAMPLE, model, context });
    setResult(response); setTechniques(response.optimizations);
  }
  function toggleContext(id: ContextKey) { setContext((items) => items.includes(id) ? items.filter((v) => v !== id) : [...items, id]); }
  async function copyPrompt() { await navigator.clipboard.writeText(result.optimized.prompt); setCopied(true); window.setTimeout(() => setCopied(false), 1600); }

  return <main>
    <section className="border-b border-border bg-surface-subtle"><div className="page-container py-10 sm:py-14">
      <PageIntro eyebrow="Optimize" title="Reduce LLM costs without reducing answer quality." description="Enter any LLM request and see exactly what can be removed, compressed, or optimized." />
      <div className="mt-7 overflow-hidden rounded-lg border border-border bg-card shadow-sm focus-within:ring-2 focus-within:ring-ring/25">
        <Textarea aria-label="LLM request" value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask anything... e.g. Explain how WebRTC works and how signaling is used in a video calling application." className="min-h-40 resize-none border-0 bg-transparent p-5 text-base leading-7 shadow-none focus-visible:ring-0 sm:min-h-44" />
        <div className="border-t border-border bg-secondary/35 p-3 sm:p-4"><div className="flex flex-col gap-3 xl:flex-row xl:items-center">
          <Select value={model} onValueChange={(v) => setModel(v as ModelId)}><SelectTrigger className="w-full bg-background sm:w-48" aria-label="Model"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="bedrock">Amazon Bedrock</SelectItem><SelectItem value="gpt">GPT</SelectItem><SelectItem value="claude">Claude</SelectItem><SelectItem value="custom">Custom Model</SelectItem></SelectContent></Select>
          <div className="flex flex-1 flex-wrap gap-2">{contextOptions.map((option) => { const active = context.includes(option.id); return <Button key={option.id} type="button" variant="outline" size="sm" className={cn("bg-background text-muted-foreground", active && "border-primary/40 bg-primary-soft text-primary")} onClick={() => toggleContext(option.id)}><option.icon />{option.label}{active ? <Check className="size-3" /> : null}</Button>; })}</div>
          <div className="flex gap-2"><Button variant="ghost" onClick={() => setQuestion(EXAMPLE)}>Load Example</Button><Button className="flex-1 px-5 sm:flex-none" onClick={analyze} disabled={stage === "analyzing"}><WandSparkles />Analyze & Optimize</Button></div>
        </div></div>
      </div>
      {stage === "analyzing" ? <AnalysisState step={step} /> : null}
    </div></section>
    {stage === "results" ? <div ref={resultsRef}><Results result={result} techniques={techniques} setTechniques={setTechniques} copied={copied} copyPrompt={copyPrompt} /></div> : null}
  </main>;
}

function AnalysisState({ step }: { step: number }) {
  const progress = Math.round((step / steps.length) * 100);
  return <div className="mt-6 rounded-lg border border-primary/20 bg-primary-soft p-5" aria-live="polite"><div className="flex items-center gap-3"><LoaderCircle className="size-5 animate-spin text-primary" /><div className="flex-1"><div className="flex justify-between text-sm font-semibold"><span>Analyzing your request...</span><span className="font-mono text-primary">{progress}%</span></div><div className="mt-3 h-1.5 overflow-hidden rounded-full bg-primary/10"><div className="h-full bg-primary transition-all duration-300" style={{ width: `${progress}%` }} /></div></div></div><div className="mt-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">{steps.map((label, index) => <div key={label} className={cn("flex items-center gap-2 text-xs transition-colors", index < step ? "text-success" : index === step ? "font-medium text-foreground" : "text-muted-foreground")} >{index < step ? <CheckCircle2 className="size-4" /> : index === step ? <LoaderCircle className="size-4 animate-spin" /> : <span className="size-4 rounded-full border border-border" />}{label}</div>)}</div></div>;
}

function Results({ result, techniques, setTechniques, copied, copyPrompt }: { result: OptimizeResponse; techniques: Technique[]; setTechniques: React.Dispatch<React.SetStateAction<Technique[]>>; copied: boolean; copyPrompt: () => void }) {
  return <>
    <section className="page-container scroll-mt-20 py-10 sm:py-14"><SectionHeading title="Optimization Results" description="Less context sent. Same answer quality verified." aside={<StatusPill><ShieldCheck className="size-3.5" /> Quality preserved</StatusPill>} />
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><MetricCard featured label="Token Reduction" value={`${result.savings.tokenReduction}%`} detail="18,420 → 5,420 input tokens" icon={Zap} /><MetricCard label="Cost Reduction" value={`${result.savings.costReduction}%`} detail="$0.00405 → $0.00128" icon={CircleDollarSign} tone="success" /><MetricCard label="Quality Score" value={`${result.quality.overall[1]}%`} detail={`Before ${result.quality.overall[0]}% · After ${result.quality.overall[1]}%`} icon={Target} tone="blue" /><MetricCard label="Latency" value={`${result.savings.latencyReduction}% faster`} detail="4.8s → 2.3s" icon={Clock3} /></div>
    </section>
    <section className="section-band"><div className="page-container"><SectionHeading title="Before vs After" description="The same request, measured end to end." /><BeforeAfter result={result} /></div></section>
    <section className="page-container py-12"><SectionHeading title="What Was Removed" description="Four targeted optimizations account for most of the savings." /><div className="grid gap-3 lg:grid-cols-2">{techniques.map((item, index) => { const Icon = techniqueIcons[item.icon]; return <div key={item.name} className={cn("rounded-lg border bg-card p-5 transition-opacity", !item.enabled && "opacity-55")}><div className="flex gap-4"><span className="flex size-9 shrink-0 items-center justify-center rounded-md bg-primary-soft text-primary"><Icon className="size-4" /></span><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center justify-between gap-2"><h3 className="font-semibold">{item.name}</h3><Switch checked={item.enabled} onCheckedChange={(enabled) => setTechniques((all) => all.map((t, i) => i === index ? { ...t, enabled } : t))} aria-label={`Toggle ${item.name}`} /></div><p className="mt-1 text-sm leading-6 text-muted-foreground">{item.description}</p><div className="mt-4 flex flex-wrap items-center gap-3 font-mono text-xs"><span>{item.beforeTokens.toLocaleString()} tokens</span><span className="text-muted-foreground">→</span><span className="text-success">{item.afterTokens.toLocaleString()} tokens</span><StatusPill>{item.savedPercent}% saved</StatusPill></div></div></div></div>; })}</div><Strategy /></section>
    <section className="section-band"><div className="page-container"><Quality result={result} /></div></section>
    <section className="page-container py-12"><AnswerComparison result={result} /></section>
    <section className="section-band"><div className="page-container"><PromptTransformation result={result} copied={copied} copyPrompt={copyPrompt} /></div></section>
    <section className="page-container py-12"><BreakdownChart result={result} /></section>
  </>;
}

function BeforeAfter({ result }: { result: OptimizeResponse }) {
  const rows = [["Input Tokens", result.original.inputTokens.toLocaleString(), result.optimized.inputTokens.toLocaleString()], ["Output Tokens", result.original.outputTokens.toLocaleString(), result.optimized.outputTokens.toLocaleString()], ["Total Tokens", result.original.totalTokens.toLocaleString(), result.optimized.totalTokens.toLocaleString()], ["Estimated Cost", `$${result.original.cost.toFixed(5)}`, `$${result.optimized.cost.toFixed(5)}`], ["Latency", `${result.original.latency} sec`, `${result.optimized.latency} sec`]];
  return <div className="overflow-hidden rounded-lg border border-border bg-card shadow-sm"><div className="grid md:grid-cols-[1fr_auto_1fr]"><div className="p-5 sm:p-7"><p className="eyebrow text-muted-foreground">Before optimization</p>{rows.map((r) => <div key={r[0]} className="flex items-center justify-between border-b border-border py-3 last:border-0"><span className="text-sm text-muted-foreground">{r[0]}</span><span className="font-mono text-sm font-semibold">{r[1]}</span></div>)}</div><div className="hidden w-px bg-border md:block" /><div className="bg-success-soft/50 p-5 sm:p-7"><p className="eyebrow text-success">After optimization</p>{rows.map((r) => <div key={r[0]} className="flex items-center justify-between border-b border-success/10 py-3 last:border-0"><span className="text-sm text-muted-foreground">{r[0]}</span><span className="font-mono text-sm font-semibold text-success">{r[2]}</span></div>)}</div></div><div className="flex items-center justify-center gap-3 border-t border-border bg-foreground px-4 py-4 text-background"><Zap className="size-5 fill-current" /><span className="font-display text-base font-bold sm:text-lg">70.6% FEWER INPUT TOKENS</span></div></div>;
}

function Strategy() { return <Collapsible className="mt-4 rounded-lg border border-border bg-card"><CollapsibleTrigger asChild><Button variant="ghost" className="h-auto w-full justify-between rounded-lg p-5 text-left"><span className="flex items-center gap-3"><Sparkles className="size-4 text-primary" />Why These Optimizations?</span><ChevronDown className="size-4" /></Button></CollapsibleTrigger><CollapsibleContent><div className="grid gap-6 border-t border-border p-5 md:grid-cols-3"><div><h4 className="text-xs font-semibold uppercase text-muted-foreground">Request analysis</h4><ul className="mt-3 space-y-2 text-sm"><li>Long conversation history detected</li><li>Irrelevant document sections detected</li><li>Multiple unused tools detected</li><li>Repeated system instructions detected</li></ul></div><div><h4 className="text-xs font-semibold uppercase text-muted-foreground">Recommended strategy</h4><ul className="mt-3 space-y-2 text-sm">{["Context Pruning", "History Summarization", "Tool Trimming", "Deduplication"].map((v) => <li key={v} className="flex gap-2"><Check className="size-4 text-success" />{v}</li>)}</ul></div><div className="rounded-md bg-primary-soft p-4"><span className="text-xs font-semibold uppercase text-primary">Estimated reduction</span><div className="mt-2 font-mono text-3xl font-semibold text-primary">64–72%</div><p className="mt-2 text-xs text-muted-foreground">With quality threshold enforced.</p></div></div></CollapsibleContent></Collapsible>; }

function Quality({ result }: { result: OptimizeResponse }) { const rows = [["Correctness", ...result.quality.correctness], ["Completeness", ...result.quality.completeness], ["Relevance", ...result.quality.relevance], ["Consistency", ...result.quality.consistency], ["Overall", ...result.quality.overall]]; const preserved = result.quality.status === "preserved"; return <div><SectionHeading title="Quality Verification" description="Before and after answers graded against the same criteria." /><div className="grid gap-5 lg:grid-cols-[1fr_0.8fr]"><div className="overflow-hidden rounded-lg border border-border bg-card"><table className="w-full text-sm"><thead className="bg-secondary/60 text-left text-xs uppercase text-muted-foreground"><tr><th className="p-3 sm:p-4">Metric</th><th className="p-3 text-right sm:p-4">Before</th><th className="p-3 text-right sm:p-4">After</th></tr></thead><tbody>{rows.map((r) => <tr key={r[0]} className={cn("border-t border-border", r[0] === "Overall" && "bg-secondary/40 font-semibold")}><td className="p-3 sm:p-4">{r[0]}</td><td className="p-3 text-right font-mono sm:p-4">{r[1]}%</td><td className="p-3 text-right font-mono text-success sm:p-4">{r[2]}%</td></tr>)}</tbody></table></div><div className={cn("flex flex-col justify-center rounded-lg border p-7", preserved ? "border-success/25 bg-success-soft" : "border-warning/25 bg-warning-soft")}><div className={cn("flex size-11 items-center justify-center rounded-full", preserved ? "bg-success text-success-foreground" : "bg-warning text-warning-foreground")}>{preserved ? <ShieldCheck /> : <Gauge />}</div><h3 className="mt-5 font-display text-xl font-bold">{preserved ? "QUALITY PRESERVED" : "Optimization rejected"}</h3><p className="mt-2 text-sm leading-6 text-muted-foreground">{preserved ? "The optimized request reduced token usage while maintaining the required answer quality." : "Quality fell below the configured threshold. Retry with a safer optimization strategy."}</p><div className="mt-6 h-2 overflow-hidden rounded-full bg-background/70"><div className="h-full bg-success" style={{ width: `${result.quality.overall[1]}%` }} /></div><div className="mt-2 flex justify-between font-mono text-xs"><span>Threshold 90%</span><span>{result.quality.overall[1]}%</span></div></div></div></div>; }

function AnswerComparison({ result }: { result: OptimizeResponse }) { return <div><SectionHeading title="Same Question. Optimized Context." description="The answers remain semantically equivalent despite a much smaller prompt." aside={<StatusPill><Target className="size-3.5" /> Semantic similarity: {result.quality.similarity}%</StatusPill>} /><div className="grid gap-4 lg:grid-cols-2"><Answer label="Original Answer" text={result.original.answer} /><Answer label="Optimized Answer" text={result.optimized.answer} optimized /></div></div>; }
function Answer({ label, text, optimized }: { label: string; text: string; optimized?: boolean }) { return <article className={cn("rounded-lg border bg-card p-5 sm:p-6", optimized && "border-success/30")}><div className="mb-4 flex items-center justify-between"><h3 className="font-semibold">{label}</h3>{optimized ? <StatusPill><Check /> Verified</StatusPill> : <StatusPill tone="neutral">Baseline</StatusPill>}</div><p className="whitespace-pre-line text-sm leading-7 text-muted-foreground">{text}</p></article>; }

function PromptTransformation({ result, copied, copyPrompt }: { result: OptimizeResponse; copied: boolean; copyPrompt: () => void }) { return <div><SectionHeading title="Prompt Transformation" description="Inspect exactly what was sent to the model." aside={<StatusPill><Scissors className="size-3.5" />70.6% smaller</StatusPill>} /><Tabs defaultValue="optimized"><div className="flex flex-col justify-between gap-3 sm:flex-row"><TabsList><TabsTrigger value="original">Original Prompt</TabsTrigger><TabsTrigger value="optimized">Optimized Prompt</TabsTrigger></TabsList><Button variant="outline" size="sm" onClick={copyPrompt}>{copied ? <Check /> : <Copy />}{copied ? "Copied" : "Copy Optimized Prompt"}</Button></div><TabsContent value="original"><CodePanel text={result.original.prompt} tokens={result.original.inputTokens} /></TabsContent><TabsContent value="optimized"><CodePanel text={result.optimized.prompt} tokens={result.optimized.inputTokens} optimized /></TabsContent></Tabs></div>; }
function CodePanel({ text, tokens, optimized }: { text: string; tokens: number; optimized?: boolean }) { return <div className="mt-4 overflow-hidden rounded-lg border border-code-border bg-code text-code-foreground"><div className="flex items-center justify-between border-b border-code-border px-4 py-3 text-xs"><span className="flex gap-1.5"><i className="size-2 rounded-full bg-bloat" /><i className="size-2 rounded-full bg-primary" /><i className="size-2 rounded-full bg-success" /></span><span className={cn("font-mono", optimized && "text-success")}>{tokens.toLocaleString()} tokens</span></div><pre className="max-h-96 overflow-auto whitespace-pre-wrap p-4 font-mono text-xs leading-6 sm:p-6">{text}</pre></div>; }

function BreakdownChart({ result }: { result: OptimizeResponse }) { return <div><SectionHeading title="Where Did We Save Tokens?" description="Input-token composition before and after optimization." /><div className="h-[340px] rounded-lg border border-border bg-card p-3 sm:p-5"><ResponsiveContainer width="100%" height="100%"><BarChart data={result.breakdown} layout="vertical" margin={{ top: 10, right: 15, left: 20, bottom: 10 }}><CartesianGrid stroke="var(--border)" horizontal={false} /><XAxis type="number" tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" /><YAxis type="category" width={112} dataKey="category" tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" /><Tooltip contentStyle={{ background: "var(--card)", border: "1px solid var(--border)", borderRadius: 6, fontSize: 12 }} /><Bar dataKey="before" name="Before" fill="var(--chart-before)" radius={[0, 3, 3, 0]} /><Bar dataKey="after" name="After" fill="var(--chart-after)" radius={[0, 3, 3, 0]} /></BarChart></ResponsiveContainer></div></div>; }
