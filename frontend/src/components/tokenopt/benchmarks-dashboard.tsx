import { useState } from "react";
import { Check, CircleDollarSign, Gauge, ListChecks, LoaderCircle, Play, Target, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { BENCHMARK_TASKS, runBenchmark } from "@/lib/tokenopt-api";
import type { BenchmarkTask } from "@/lib/tokenopt-types";
import { PageIntro } from "./app-shell";
import { MetricCard, StatusPill } from "./shared";

export function BenchmarksDashboard() {
  const [tasks, setTasks] = useState<BenchmarkTask[]>(BENCHMARK_TASKS);
  const [running, setRunning] = useState(false);
  async function run() { setRunning(true); setTasks((rows) => rows.map((r) => ({ ...r, status: "running" }))); const next = await runBenchmark(); window.setTimeout(() => { setTasks(next); setRunning(false); }, 700); }
  return <main className="page-container py-10 sm:py-14"><PageIntro eyebrow="Fixed workload" title="Benchmark" description="Evaluate optimization performance across 10 representative tasks without changing the workload." action={<Button onClick={run} disabled={running}>{running ? <LoaderCircle className="animate-spin" /> : <Play className="fill-current" />}{running ? "Running benchmark..." : "Run Benchmark"}</Button>} />
    <div className="mt-7 grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><MetricCard label="Total Tasks" value="10" detail="Fixed benchmark workload" icon={ListChecks} /><MetricCard featured label="Avg. Token Reduction" value="62.4%" detail="Across all task types" icon={Zap} /><MetricCard label="Avg. Cost Reduction" value="58.7%" detail="Model-adjusted estimate" icon={CircleDollarSign} tone="success" /><MetricCard label="Average Quality" value="94.8%" detail="Required threshold: 90%" icon={Target} tone="blue" /></div>
    <section className="mt-8"><div className="mb-4 flex items-center justify-between"><div><h2 className="text-xl font-semibold">Task Results</h2><p className="mt-1 text-sm text-muted-foreground">Same tasks, before and after optimization.</p></div><StatusPill><Gauge className="size-3.5" /> All checks passed</StatusPill></div>
      <div className="overflow-x-auto rounded-lg border border-border bg-card"><table className="w-full min-w-[760px] text-sm"><thead className="bg-secondary/60 text-left text-xs uppercase text-muted-foreground"><tr><th className="p-4">Task</th><th className="p-4">Type</th><th className="p-4 text-right">Before</th><th className="p-4 text-right">After</th><th className="p-4 text-right">Saved</th><th className="p-4 text-right">Quality</th><th className="p-4 text-center">Status</th></tr></thead><tbody>{tasks.map((task) => <tr key={task.id} className="border-t border-border"><td className="p-4 font-mono font-semibold">{task.id}</td><td className="p-4">{task.type}</td><td className="p-4 text-right font-mono text-muted-foreground">{task.before.toLocaleString()}</td><td className="p-4 text-right font-mono">{task.after.toLocaleString()}</td><td className="p-4 text-right font-mono font-semibold text-success">{task.saved}%</td><td className="p-4 text-right font-mono">{task.quality}%</td><td className="p-4 text-center">{task.status === "running" ? <LoaderCircle className="mx-auto size-4 animate-spin text-primary" /> : <span className="inline-flex size-6 items-center justify-center rounded-full bg-success-soft text-success"><Check className="size-3.5" /></span>}</td></tr>)}</tbody></table></div>
    </section>
  </main>;
}
