import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime, n as CollapsibleTrigger$1, r as Root, t as CollapsibleContent$1 } from "../_libs/@radix-ui/react-collapsible+[...].mjs";
import { S as CircleCheck, T as Check, _ as Gauge, a as Target, b as Clock3, g as History, h as Layers, i as WandSparkles, l as Scissors, o as Sparkles, p as LoaderCircle, r as Wrench, s as ShieldCheck, t as Zap, v as Files, w as ChevronDown, x as CircleDollarSign, y as Copy } from "../_libs/lucide-react.mjs";
import { i as cn, n as Button, r as PageIntro } from "./app-shell-BQIYZ9b5.mjs";
import { a as SelectValue, i as SelectTrigger, n as SelectContent, r as SelectItem, t as Select } from "./select-DpxQJvzk.mjs";
import { a as SectionHeading, c as optimizeRequest, i as MetricCard, n as MOCK_OPTIMIZATION, o as StatusPill } from "./shared-CMioEdlO.mjs";
import { c as ResponsiveContainer, i as XAxis, l as Tooltip, o as CartesianGrid, r as YAxis, s as Bar, t as BarChart } from "../_libs/recharts+[...].mjs";
import { t as Switch } from "./switch-DVo0Penr.mjs";
import { i as Trigger, n as List, r as Root2, t as Content } from "../_libs/radix-ui__react-tabs.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/routes-keuR4qz4.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var Collapsible = Root;
var CollapsibleTrigger = CollapsibleTrigger$1;
var CollapsibleContent = CollapsibleContent$1;
var Tabs = Root2;
var TabsList = import_react.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(List, {
	ref,
	className: cn("inline-flex h-9 items-center justify-center rounded-lg bg-muted p-1 text-muted-foreground", className),
	...props
}));
TabsList.displayName = List.displayName;
var TabsTrigger = import_react.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Trigger, {
	ref,
	className: cn("inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1 text-sm font-medium ring-offset-background cursor-pointer transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 disabled:cursor-not-allowed data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow", className),
	...props
}));
TabsTrigger.displayName = Trigger.displayName;
var TabsContent = import_react.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Content, {
	ref,
	className: cn("mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2", className),
	...props
}));
TabsContent.displayName = Content.displayName;
var Textarea = import_react.forwardRef(({ className, ...props }, ref) => {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("textarea", {
		className: cn("flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-base shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm", className),
		ref,
		...props
	});
});
Textarea.displayName = "Textarea";
var EXAMPLE = "Explain how WebRTC works and how signaling is used in a video calling application.";
var steps = [
	"Parsing request",
	"Counting original tokens",
	"Finding relevant context",
	"Removing duplicate instructions",
	"Selecting required tools",
	"Compressing conversation history",
	"Generating optimized prompt",
	"Running quality check"
];
var contextOptions = [
	{
		id: "history",
		label: "Conversation History",
		icon: History
	},
	{
		id: "documents",
		label: "Documents",
		icon: Files
	},
	{
		id: "tools",
		label: "Tool Definitions",
		icon: Wrench
	}
];
var techniqueIcons = {
	prune: Scissors,
	history: History,
	tools: Wrench,
	dedupe: Layers
};
function OptimizeDashboard() {
	const [question, setQuestion] = (0, import_react.useState)("");
	const [model, setModel] = (0, import_react.useState)("bedrock");
	const [context, setContext] = (0, import_react.useState)([
		"history",
		"documents",
		"tools"
	]);
	const [stage, setStage] = (0, import_react.useState)("input");
	const [step, setStep] = (0, import_react.useState)(0);
	const [result, setResult] = (0, import_react.useState)(MOCK_OPTIMIZATION);
	const [techniques, setTechniques] = (0, import_react.useState)(MOCK_OPTIMIZATION.optimizations);
	const [copied, setCopied] = (0, import_react.useState)(false);
	const resultsRef = (0, import_react.useRef)(null);
	(0, import_react.useEffect)(() => {
		if (stage !== "analyzing") return;
		if (step < steps.length) {
			const timer = window.setTimeout(() => setStep((v) => v + 1), 260);
			return () => window.clearTimeout(timer);
		}
		const timer = window.setTimeout(() => {
			setStage("results");
			requestAnimationFrame(() => resultsRef.current?.scrollIntoView({
				behavior: "smooth",
				block: "start"
			}));
		}, 300);
		return () => window.clearTimeout(timer);
	}, [stage, step]);
	async function analyze() {
		if (!question.trim()) setQuestion(EXAMPLE);
		setStage("analyzing");
		setStep(0);
		const response = await optimizeRequest({
			question: question.trim() || EXAMPLE,
			model,
			context
		});
		setResult(response);
		setTechniques(response.optimizations);
	}
	function toggleContext(id) {
		setContext((items) => items.includes(id) ? items.filter((v) => v !== id) : [...items, id]);
	}
	async function copyPrompt() {
		await navigator.clipboard.writeText(result.optimized.prompt);
		setCopied(true);
		window.setTimeout(() => setCopied(false), 1600);
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
		className: "border-b border-border bg-surface-subtle",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "page-container py-10 sm:py-14",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PageIntro, {
					eyebrow: "Optimize",
					title: "Reduce LLM costs without reducing answer quality.",
					description: "Enter any LLM request and see exactly what can be removed, compressed, or optimized."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-7 overflow-hidden rounded-lg border border-border bg-card shadow-sm focus-within:ring-2 focus-within:ring-ring/25",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Textarea, {
						"aria-label": "LLM request",
						value: question,
						onChange: (e) => setQuestion(e.target.value),
						placeholder: "Ask anything... e.g. Explain how WebRTC works and how signaling is used in a video calling application.",
						className: "min-h-40 resize-none border-0 bg-transparent p-5 text-base leading-7 shadow-none focus-visible:ring-0 sm:min-h-44"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "border-t border-border bg-secondary/35 p-3 sm:p-4",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex flex-col gap-3 xl:flex-row xl:items-center",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Select, {
									value: model,
									onValueChange: (v) => setModel(v),
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectTrigger, {
										className: "w-full bg-background sm:w-48",
										"aria-label": "Model",
										children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectValue, {})
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SelectContent, { children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
											value: "bedrock",
											children: "Amazon Bedrock"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
											value: "gpt",
											children: "GPT"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
											value: "claude",
											children: "Claude"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
											value: "custom",
											children: "Custom Model"
										})
									] })]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "flex flex-1 flex-wrap gap-2",
									children: contextOptions.map((option) => {
										const active = context.includes(option.id);
										return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
											type: "button",
											variant: "outline",
											size: "sm",
											className: cn("bg-background text-muted-foreground", active && "border-primary/40 bg-primary-soft text-primary"),
											onClick: () => toggleContext(option.id),
											children: [
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)(option.icon, {}),
												option.label,
												active ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "size-3" }) : null
											]
										}, option.id);
									})
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex gap-2",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
										variant: "ghost",
										onClick: () => setQuestion(EXAMPLE),
										children: "Load Example"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
										className: "flex-1 px-5 sm:flex-none",
										onClick: analyze,
										disabled: stage === "analyzing",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(WandSparkles, {}), "Analyze & Optimize"]
									})]
								})
							]
						})
					})]
				}),
				stage === "analyzing" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AnalysisState, { step }) : null
			]
		})
	}), stage === "results" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		ref: resultsRef,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Results, {
			result,
			techniques,
			setTechniques,
			copied,
			copyPrompt
		})
	}) : null] });
}
function AnalysisState({ step }) {
	const progress = Math.round(step / steps.length * 100);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "mt-6 rounded-lg border border-primary/20 bg-primary-soft p-5",
		"aria-live": "polite",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-center gap-3",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "size-5 animate-spin text-primary" }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex-1",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex justify-between text-sm font-semibold",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "Analyzing your request..." }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "font-mono text-primary",
						children: [progress, "%"]
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-3 h-1.5 overflow-hidden rounded-full bg-primary/10",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "h-full bg-primary transition-all duration-300",
						style: { width: `${progress}%` }
					})
				})]
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "mt-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-4",
			children: steps.map((label, index) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: cn("flex items-center gap-2 text-xs transition-colors", index < step ? "text-success" : index === step ? "font-medium text-foreground" : "text-muted-foreground"),
				children: [index < step ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleCheck, { className: "size-4" }) : index === step ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "size-4 animate-spin" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-4 rounded-full border border-border" }), label]
			}, label))
		})]
	});
}
function Results({ result, techniques, setTechniques, copied, copyPrompt }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
		/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
			className: "page-container scroll-mt-20 py-10 sm:py-14",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SectionHeading, {
				title: "Optimization Results",
				description: "Less context sent. Same answer quality verified.",
				aside: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(StatusPill, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldCheck, { className: "size-3.5" }), " Quality preserved"] })
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid gap-3 sm:grid-cols-2 lg:grid-cols-4",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MetricCard, {
						featured: true,
						label: "Token Reduction",
						value: `${result.savings.tokenReduction}%`,
						detail: "18,420 → 5,420 input tokens",
						icon: Zap
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MetricCard, {
						label: "Cost Reduction",
						value: `${result.savings.costReduction}%`,
						detail: "$0.00405 → $0.00128",
						icon: CircleDollarSign,
						tone: "success"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MetricCard, {
						label: "Quality Score",
						value: `${result.quality.overall[1]}%`,
						detail: `Before ${result.quality.overall[0]}% · After ${result.quality.overall[1]}%`,
						icon: Target,
						tone: "blue"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MetricCard, {
						label: "Latency",
						value: `${result.savings.latencyReduction}% faster`,
						detail: "4.8s → 2.3s",
						icon: Clock3
					})
				]
			})]
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
			className: "section-band",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "page-container",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SectionHeading, {
					title: "Before vs After",
					description: "The same request, measured end to end."
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(BeforeAfter, { result })]
			})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
			className: "page-container py-12",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SectionHeading, {
					title: "What Was Removed",
					description: "Four targeted optimizations account for most of the savings."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "grid gap-3 lg:grid-cols-2",
					children: techniques.map((item, index) => {
						const Icon = techniqueIcons[item.icon];
						return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: cn("rounded-lg border bg-card p-5 transition-opacity", !item.enabled && "opacity-55"),
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex gap-4",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "flex size-9 shrink-0 items-center justify-center rounded-md bg-primary-soft text-primary",
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Icon, { className: "size-4" })
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "min-w-0 flex-1",
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
											className: "flex flex-wrap items-center justify-between gap-2",
											children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
												className: "font-semibold",
												children: item.name
											}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Switch, {
												checked: item.enabled,
												onCheckedChange: (enabled) => setTechniques((all) => all.map((t, i) => i === index ? {
													...t,
													enabled
												} : t)),
												"aria-label": `Toggle ${item.name}`
											})]
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
											className: "mt-1 text-sm leading-6 text-muted-foreground",
											children: item.description
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
											className: "mt-4 flex flex-wrap items-center gap-3 font-mono text-xs",
											children: [
												/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: [item.beforeTokens.toLocaleString(), " tokens"] }),
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
													className: "text-muted-foreground",
													children: "→"
												}),
												/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
													className: "text-success",
													children: [item.afterTokens.toLocaleString(), " tokens"]
												}),
												/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(StatusPill, { children: [item.savedPercent, "% saved"] })
											]
										})
									]
								})]
							})
						}, item.name);
					})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Strategy, {})
			]
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
			className: "section-band",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "page-container",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Quality, { result })
			})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
			className: "page-container py-12",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AnswerComparison, { result })
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
			className: "section-band",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "page-container",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(PromptTransformation, {
					result,
					copied,
					copyPrompt
				})
			})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
			className: "page-container py-12",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(BreakdownChart, { result })
		})
	] });
}
function BeforeAfter({ result }) {
	const rows = [
		[
			"Input Tokens",
			result.original.inputTokens.toLocaleString(),
			result.optimized.inputTokens.toLocaleString()
		],
		[
			"Output Tokens",
			result.original.outputTokens.toLocaleString(),
			result.optimized.outputTokens.toLocaleString()
		],
		[
			"Total Tokens",
			result.original.totalTokens.toLocaleString(),
			result.optimized.totalTokens.toLocaleString()
		],
		[
			"Estimated Cost",
			`$${result.original.cost.toFixed(5)}`,
			`$${result.optimized.cost.toFixed(5)}`
		],
		[
			"Latency",
			`${result.original.latency} sec`,
			`${result.optimized.latency} sec`
		]
	];
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "overflow-hidden rounded-lg border border-border bg-card shadow-sm",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "grid md:grid-cols-[1fr_auto_1fr]",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "p-5 sm:p-7",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow text-muted-foreground",
						children: "Before optimization"
					}), rows.map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center justify-between border-b border-border py-3 last:border-0",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-sm text-muted-foreground",
							children: r[0]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-mono text-sm font-semibold",
							children: r[1]
						})]
					}, r[0]))]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "hidden w-px bg-border md:block" }),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "bg-success-soft/50 p-5 sm:p-7",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "eyebrow text-success",
						children: "After optimization"
					}), rows.map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center justify-between border-b border-success/10 py-3 last:border-0",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-sm text-muted-foreground",
							children: r[0]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-mono text-sm font-semibold text-success",
							children: r[2]
						})]
					}, r[0]))]
				})
			]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-center justify-center gap-3 border-t border-border bg-foreground px-4 py-4 text-background",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Zap, { className: "size-5 fill-current" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "font-display text-base font-bold sm:text-lg",
				children: "70.6% FEWER INPUT TOKENS"
			})]
		})]
	});
}
function Strategy() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Collapsible, {
		className: "mt-4 rounded-lg border border-border bg-card",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CollapsibleTrigger, {
			asChild: true,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
				variant: "ghost",
				className: "h-auto w-full justify-between rounded-lg p-5 text-left",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
					className: "flex items-center gap-3",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Sparkles, { className: "size-4 text-primary" }), "Why These Optimizations?"]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronDown, { className: "size-4" })]
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CollapsibleContent, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "grid gap-6 border-t border-border p-5 md:grid-cols-3",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h4", {
					className: "text-xs font-semibold uppercase text-muted-foreground",
					children: "Request analysis"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("ul", {
					className: "mt-3 space-y-2 text-sm",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: "Long conversation history detected" }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: "Irrelevant document sections detected" }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: "Multiple unused tools detected" }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: "Repeated system instructions detected" })
					]
				})] }),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h4", {
					className: "text-xs font-semibold uppercase text-muted-foreground",
					children: "Recommended strategy"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
					className: "mt-3 space-y-2 text-sm",
					children: [
						"Context Pruning",
						"History Summarization",
						"Tool Trimming",
						"Deduplication"
					].map((v) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
						className: "flex gap-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "size-4 text-success" }), v]
					}, v))
				})] }),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "rounded-md bg-primary-soft p-4",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-xs font-semibold uppercase text-primary",
							children: "Estimated reduction"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "mt-2 font-mono text-3xl font-semibold text-primary",
							children: "64–72%"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-2 text-xs text-muted-foreground",
							children: "With quality threshold enforced."
						})
					]
				})
			]
		}) })]
	});
}
function Quality({ result }) {
	const rows = [
		["Correctness", ...result.quality.correctness],
		["Completeness", ...result.quality.completeness],
		["Relevance", ...result.quality.relevance],
		["Consistency", ...result.quality.consistency],
		["Overall", ...result.quality.overall]
	];
	const preserved = result.quality.status === "preserved";
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SectionHeading, {
		title: "Quality Verification",
		description: "Before and after answers graded against the same criteria."
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "grid gap-5 lg:grid-cols-[1fr_0.8fr]",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "overflow-hidden rounded-lg border border-border bg-card",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("table", {
				className: "w-full text-sm",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("thead", {
					className: "bg-secondary/60 text-left text-xs uppercase text-muted-foreground",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", { children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
							className: "p-3 sm:p-4",
							children: "Metric"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
							className: "p-3 text-right sm:p-4",
							children: "Before"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
							className: "p-3 text-right sm:p-4",
							children: "After"
						})
					] })
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tbody", { children: rows.map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", {
					className: cn("border-t border-border", r[0] === "Overall" && "bg-secondary/40 font-semibold"),
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
							className: "p-3 sm:p-4",
							children: r[0]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("td", {
							className: "p-3 text-right font-mono sm:p-4",
							children: [r[1], "%"]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("td", {
							className: "p-3 text-right font-mono text-success sm:p-4",
							children: [r[2], "%"]
						})
					]
				}, r[0])) })]
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: cn("flex flex-col justify-center rounded-lg border p-7", preserved ? "border-success/25 bg-success-soft" : "border-warning/25 bg-warning-soft"),
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: cn("flex size-11 items-center justify-center rounded-full", preserved ? "bg-success text-success-foreground" : "bg-warning text-warning-foreground"),
					children: preserved ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldCheck, {}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Gauge, {})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
					className: "mt-5 font-display text-xl font-bold",
					children: preserved ? "QUALITY PRESERVED" : "Optimization rejected"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-2 text-sm leading-6 text-muted-foreground",
					children: preserved ? "The optimized request reduced token usage while maintaining the required answer quality." : "Quality fell below the configured threshold. Retry with a safer optimization strategy."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-6 h-2 overflow-hidden rounded-full bg-background/70",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "h-full bg-success",
						style: { width: `${result.quality.overall[1]}%` }
					})
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-2 flex justify-between font-mono text-xs",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "Threshold 90%" }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: [result.quality.overall[1], "%"] })]
				})
			]
		})]
	})] });
}
function AnswerComparison({ result }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SectionHeading, {
		title: "Same Question. Optimized Context.",
		description: "The answers remain semantically equivalent despite a much smaller prompt.",
		aside: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(StatusPill, { children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Target, { className: "size-3.5" }),
			" Semantic similarity: ",
			result.quality.similarity,
			"%"
		] })
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "grid gap-4 lg:grid-cols-2",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Answer, {
			label: "Original Answer",
			text: result.original.answer
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Answer, {
			label: "Optimized Answer",
			text: result.optimized.answer,
			optimized: true
		})]
	})] });
}
function Answer({ label, text, optimized }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
		className: cn("rounded-lg border bg-card p-5 sm:p-6", optimized && "border-success/30"),
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "mb-4 flex items-center justify-between",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
				className: "font-semibold",
				children: label
			}), optimized ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(StatusPill, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, {}), " Verified"] }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatusPill, {
				tone: "neutral",
				children: "Baseline"
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "whitespace-pre-line text-sm leading-7 text-muted-foreground",
			children: text
		})]
	});
}
function PromptTransformation({ result, copied, copyPrompt }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SectionHeading, {
		title: "Prompt Transformation",
		description: "Inspect exactly what was sent to the model.",
		aside: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(StatusPill, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Scissors, { className: "size-3.5" }), "70.6% smaller"] })
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Tabs, {
		defaultValue: "optimized",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-col justify-between gap-3 sm:flex-row",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TabsList, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsTrigger, {
					value: "original",
					children: "Original Prompt"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsTrigger, {
					value: "optimized",
					children: "Optimized Prompt"
				})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
					variant: "outline",
					size: "sm",
					onClick: copyPrompt,
					children: [copied ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, {}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Copy, {}), copied ? "Copied" : "Copy Optimized Prompt"]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsContent, {
				value: "original",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CodePanel, {
					text: result.original.prompt,
					tokens: result.original.inputTokens
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TabsContent, {
				value: "optimized",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CodePanel, {
					text: result.optimized.prompt,
					tokens: result.optimized.inputTokens,
					optimized: true
				})
			})
		]
	})] });
}
function CodePanel({ text, tokens, optimized }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "mt-4 overflow-hidden rounded-lg border border-code-border bg-code text-code-foreground",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-center justify-between border-b border-code-border px-4 py-3 text-xs",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
				className: "flex gap-1.5",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("i", { className: "size-2 rounded-full bg-bloat" }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("i", { className: "size-2 rounded-full bg-primary" }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("i", { className: "size-2 rounded-full bg-success" })
				]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
				className: cn("font-mono", optimized && "text-success"),
				children: [tokens.toLocaleString(), " tokens"]
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
			className: "max-h-96 overflow-auto whitespace-pre-wrap p-4 font-mono text-xs leading-6 sm:p-6",
			children: text
		})]
	});
}
function BreakdownChart({ result }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SectionHeading, {
		title: "Where Did We Save Tokens?",
		description: "Input-token composition before and after optimization."
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "h-[340px] rounded-lg border border-border bg-card p-3 sm:p-5",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
			width: "100%",
			height: "100%",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(BarChart, {
				data: result.breakdown,
				layout: "vertical",
				margin: {
					top: 10,
					right: 15,
					left: 20,
					bottom: 10
				},
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CartesianGrid, {
						stroke: "var(--border)",
						horizontal: false
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
						type: "number",
						tick: { fontSize: 11 },
						stroke: "var(--muted-foreground)"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
						type: "category",
						width: 112,
						dataKey: "category",
						tick: { fontSize: 11 },
						stroke: "var(--muted-foreground)"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { contentStyle: {
						background: "var(--card)",
						border: "1px solid var(--border)",
						borderRadius: 6,
						fontSize: 12
					} }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
						dataKey: "before",
						name: "Before",
						fill: "var(--chart-before)",
						radius: [
							0,
							3,
							3,
							0
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
						dataKey: "after",
						name: "After",
						fill: "var(--chart-after)",
						radius: [
							0,
							3,
							3,
							0
						]
					})
				]
			})
		})
	})] });
}
var SplitComponent = OptimizeDashboard;
//#endregion
export { SplitComponent as component };
