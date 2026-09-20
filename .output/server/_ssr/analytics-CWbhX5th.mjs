import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-collapsible+[...].mjs";
import { E as ChartColumn, d as PiggyBank, t as Zap } from "../_libs/lucide-react.mjs";
import { r as PageIntro } from "./app-shell-BQIYZ9b5.mjs";
import { t as Input } from "./input-BR4Q3CEJ.mjs";
import { a as SelectValue, i as SelectTrigger, n as SelectContent, r as SelectItem, t as Select } from "./select-DpxQJvzk.mjs";
import { a as SectionHeading, i as MetricCard, r as MODEL_PRICING, s as estimateCost } from "./shared-CMioEdlO.mjs";
import { a as Line, c as ResponsiveContainer, i as XAxis, l as Tooltip, n as LineChart, o as CartesianGrid, r as YAxis, s as Bar, t as BarChart } from "../_libs/recharts+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/analytics-CWbhX5th.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var pareto = [
	{
		name: "No optimization",
		tokens: 18420,
		quality: 95.2
	},
	{
		name: "Deduplication",
		tokens: 15600,
		quality: 95.3
	},
	{
		name: "Context pruning",
		tokens: 11400,
		quality: 95.1
	},
	{
		name: "History summary",
		tokens: 8100,
		quality: 94.9
	},
	{
		name: "Tool trimming",
		tokens: 6500,
		quality: 95.1
	},
	{
		name: "Full optimization",
		tokens: 5420,
		quality: 95.5
	}
];
var fmtMoney = (n) => new Intl.NumberFormat("en-US", {
	style: "currency",
	currency: "USD",
	maximumFractionDigits: 0
}).format(n);
var compact = (n) => new Intl.NumberFormat("en-US", {
	notation: "compact",
	maximumFractionDigits: 1
}).format(n);
function AnalyticsDashboard() {
	const [requests, setRequests] = (0, import_react.useState)(1e6);
	const [inputTokens, setInputTokens] = (0, import_react.useState)(25e3);
	const [outputTokens, setOutputTokens] = (0, import_react.useState)(1e3);
	const [model, setModel] = (0, import_react.useState)("bedrock");
	const estimate = (0, import_react.useMemo)(() => estimateCost({
		requests,
		inputTokens,
		outputTokens,
		model
	}), [
		requests,
		inputTokens,
		outputTokens,
		model
	]);
	const requestData = [
		.25,
		.5,
		.75,
		1
	].map((ratio) => ({
		requests: `${ratio}M`,
		before: estimate.beforeCost * ratio,
		after: estimate.afterCost * ratio
	}));
	const tokenData = [{
		name: "Without TokenOpt",
		tokens: estimate.beforeTokens / 1e9
	}, {
		name: "With TokenOpt",
		tokens: estimate.afterTokens / 1e9
	}];
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "page-container py-10 sm:py-14",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PageIntro, {
				eyebrow: "Analytics",
				title: "Cost Simulator",
				description: "Model your token volume, compare operating costs, and explore the quality-efficiency frontier."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "mt-7 grid gap-6 lg:grid-cols-[0.8fr_1.2fr]",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "rounded-lg border border-border bg-card p-5",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
							className: "font-semibold",
							children: "Workload assumptions"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "mt-5 space-y-4",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
									label: "Monthly Requests",
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
										type: "number",
										min: "0",
										value: requests,
										onChange: (e) => setRequests(Number(e.target.value) || 0)
									})
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
									label: "Average Input Tokens",
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
										type: "number",
										min: "0",
										value: inputTokens,
										onChange: (e) => setInputTokens(Number(e.target.value) || 0)
									})
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
									label: "Average Output Tokens",
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
										type: "number",
										min: "0",
										value: outputTokens,
										onChange: (e) => setOutputTokens(Number(e.target.value) || 0)
									})
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Field, {
									label: "Model",
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Select, {
										value: model,
										onValueChange: (v) => setModel(v),
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectTrigger, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectValue, {}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectContent, { children: Object.entries(MODEL_PRICING).map(([id, p]) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
											value: id,
											children: p.label
										}, id)) })]
									})
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-5 border-t border-border pt-4 text-xs leading-5 text-muted-foreground",
							children: "Pricing is configurable by model and kept outside the interface calculations."
						})
					]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "grid gap-3 sm:grid-cols-2",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MetricCard, {
							label: "Without TokenOpt",
							value: `${compact(estimate.beforeTokens)} tokens`,
							detail: `${fmtMoney(estimate.beforeCost)} / month`,
							icon: ChartColumn
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MetricCard, {
							label: "With TokenOpt",
							value: `${compact(estimate.afterTokens)} tokens`,
							detail: `${fmtMoney(estimate.afterCost)} / month`,
							icon: Zap,
							tone: "success"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "metric-card metric-card-featured sm:col-span-2",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center justify-between",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "text-xs font-semibold uppercase text-muted-foreground",
										children: "Estimated Savings"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(PiggyBank, { className: "size-5 text-primary" })]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "mt-4 font-mono text-4xl font-semibold text-primary",
									children: [
										fmtMoney(estimate.monthlySavings),
										" ",
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "text-base text-muted-foreground",
											children: "/ month"
										})
									]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
									className: "mt-2 text-sm text-muted-foreground",
									children: [fmtMoney(estimate.monthlySavings * 12), " / year"]
								})
							]
						})
					]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "mt-12",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SectionHeading, {
					title: "Cost & Volume",
					description: "Projected savings scale with request volume."
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "grid gap-4 lg:grid-cols-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChartCard, {
						title: "Requests vs Cost",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
							width: "100%",
							height: "100%",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(LineChart, {
								data: requestData,
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CartesianGrid, { stroke: "var(--border)" }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
										dataKey: "requests",
										tick: { fontSize: 11 }
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
										tickFormatter: compact,
										tick: { fontSize: 11 }
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, {
										formatter: (v) => fmtMoney(v),
										contentStyle: {
											background: "var(--card)",
											border: "1px solid var(--border)",
											borderRadius: 6
										}
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Line, {
										type: "monotone",
										dataKey: "before",
										stroke: "var(--chart-before)",
										strokeWidth: 2
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Line, {
										type: "monotone",
										dataKey: "after",
										stroke: "var(--chart-after)",
										strokeWidth: 2
									})
								]
							})
						})
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChartCard, {
						title: "Tokens Before vs After",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
							width: "100%",
							height: "100%",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(BarChart, {
								data: tokenData,
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CartesianGrid, {
										stroke: "var(--border)",
										vertical: false
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
										dataKey: "name",
										tick: { fontSize: 11 }
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
										tick: { fontSize: 11 },
										unit: "B"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { contentStyle: {
										background: "var(--card)",
										border: "1px solid var(--border)",
										borderRadius: 6
									} }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
										dataKey: "tokens",
										fill: "var(--chart-after)",
										radius: [
											4,
											4,
											0,
											0
										]
									})
								]
							})
						})
					})]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "mt-12",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SectionHeading, {
					title: "Quality vs Token Usage",
					description: "Each optimization level reduces context while quality remains above threshold."
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChartCard, {
					title: "Pareto curve",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
						width: "100%",
						height: "100%",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(LineChart, {
							data: [...pareto].reverse(),
							margin: {
								left: 10,
								right: 20
							},
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CartesianGrid, { stroke: "var(--border)" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
									dataKey: "tokens",
									type: "number",
									domain: [4e3, 2e4],
									tick: { fontSize: 11 }
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
									domain: [90, 100],
									tick: { fontSize: 11 },
									unit: "%"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { contentStyle: {
									background: "var(--card)",
									border: "1px solid var(--border)",
									borderRadius: 6
								} }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Line, {
									type: "monotone",
									dataKey: "quality",
									stroke: "var(--primary)",
									strokeWidth: 3,
									dot: {
										fill: "var(--primary)",
										r: 5
									}
								})
							]
						})
					})
				})]
			})
		]
	});
}
function Field({ label, children }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
		className: "block",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "mb-1.5 block text-xs font-semibold text-muted-foreground",
			children: label
		}), children]
	});
}
function ChartCard({ title, children }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "rounded-lg border border-border bg-card p-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
			className: "mb-3 text-sm font-semibold",
			children: title
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "h-72",
			children
		})]
	});
}
var SplitComponent = AnalyticsDashboard;
//#endregion
export { SplitComponent as component };
