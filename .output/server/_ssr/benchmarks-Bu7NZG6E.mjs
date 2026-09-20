import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-collapsible+[...].mjs";
import { T as Check, _ as Gauge, a as Target, m as ListChecks, p as LoaderCircle, t as Zap, u as Play, x as CircleDollarSign } from "../_libs/lucide-react.mjs";
import { n as Button, r as PageIntro } from "./app-shell-BQIYZ9b5.mjs";
import { i as MetricCard, l as runBenchmark, o as StatusPill, t as BENCHMARK_TASKS } from "./shared-CMioEdlO.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/benchmarks-Bu7NZG6E.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function BenchmarksDashboard() {
	const [tasks, setTasks] = (0, import_react.useState)(BENCHMARK_TASKS);
	const [running, setRunning] = (0, import_react.useState)(false);
	async function run() {
		setRunning(true);
		setTasks((rows) => rows.map((r) => ({
			...r,
			status: "running"
		})));
		const next = await runBenchmark();
		window.setTimeout(() => {
			setTasks(next);
			setRunning(false);
		}, 700);
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "page-container py-10 sm:py-14",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PageIntro, {
				eyebrow: "Fixed workload",
				title: "Benchmark",
				description: "Evaluate optimization performance across 10 representative tasks without changing the workload.",
				action: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
					onClick: run,
					disabled: running,
					children: [running ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "animate-spin" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Play, { className: "fill-current" }), running ? "Running benchmark..." : "Run Benchmark"]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-7 grid gap-3 sm:grid-cols-2 lg:grid-cols-4",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MetricCard, {
						label: "Total Tasks",
						value: "10",
						detail: "Fixed benchmark workload",
						icon: ListChecks
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MetricCard, {
						featured: true,
						label: "Avg. Token Reduction",
						value: "62.4%",
						detail: "Across all task types",
						icon: Zap
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MetricCard, {
						label: "Avg. Cost Reduction",
						value: "58.7%",
						detail: "Model-adjusted estimate",
						icon: CircleDollarSign,
						tone: "success"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MetricCard, {
						label: "Average Quality",
						value: "94.8%",
						detail: "Required threshold: 90%",
						icon: Target,
						tone: "blue"
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "mt-8",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mb-4 flex items-center justify-between",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "text-xl font-semibold",
						children: "Task Results"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-1 text-sm text-muted-foreground",
						children: "Same tasks, before and after optimization."
					})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(StatusPill, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Gauge, { className: "size-3.5" }), " All checks passed"] })]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "overflow-x-auto rounded-lg border border-border bg-card",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("table", {
						className: "w-full min-w-[760px] text-sm",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("thead", {
							className: "bg-secondary/60 text-left text-xs uppercase text-muted-foreground",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", { children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
									className: "p-4",
									children: "Task"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
									className: "p-4",
									children: "Type"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
									className: "p-4 text-right",
									children: "Before"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
									className: "p-4 text-right",
									children: "After"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
									className: "p-4 text-right",
									children: "Saved"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
									className: "p-4 text-right",
									children: "Quality"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
									className: "p-4 text-center",
									children: "Status"
								})
							] })
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tbody", { children: tasks.map((task) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", {
							className: "border-t border-border",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "p-4 font-mono font-semibold",
									children: task.id
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "p-4",
									children: task.type
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "p-4 text-right font-mono text-muted-foreground",
									children: task.before.toLocaleString()
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "p-4 text-right font-mono",
									children: task.after.toLocaleString()
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("td", {
									className: "p-4 text-right font-mono font-semibold text-success",
									children: [task.saved, "%"]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("td", {
									className: "p-4 text-right font-mono",
									children: [task.quality, "%"]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
									className: "p-4 text-center",
									children: task.status === "running" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "mx-auto size-4 animate-spin text-primary" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "inline-flex size-6 items-center justify-center rounded-full bg-success-soft text-success",
										children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "size-3.5" })
									})
								})
							]
						}, task.id)) })]
					})
				})]
			})
		]
	});
}
var SplitComponent = BenchmarksDashboard;
//#endregion
export { SplitComponent as component };
