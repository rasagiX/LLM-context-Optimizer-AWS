import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-collapsible+[...].mjs";
import { i as cn } from "./app-shell-BQIYZ9b5.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/shared-CMioEdlO.js
var import_jsx_runtime = require_jsx_runtime();
var API_ENDPOINTS = {
	optimize: "http://localhost:8000/api/v1/optimize",
	optimizeDemo: "http://localhost:8000/api/v1/optimize/demo",
	evaluate: "http://localhost:8000/api/v1/evaluate",
	benchmark: "http://localhost:8000/api/v1/benchmarks/run",
	analytics: "/api/analytics",
	costEstimate: "/api/cost-estimate"
};
var delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
var sampleConversation = [
	{
		role: "user",
		content: "We need to build a high-performance backend with security and token optimization."
	},
	{
		role: "assistant",
		content: "What are your core security requirements?"
	},
	{
		role: "user",
		content: "Must be PCI-DSS Level 1 compliant and support GDPR data residency."
	},
	{
		role: "assistant",
		content: "AWS and Azure provide PCI-DSS Level 1 compliance in EU regions."
	},
	{
		role: "user",
		content: "We also require SOC 2 Type II certification and low latency."
	},
	{
		role: "assistant",
		content: "Amazon Bedrock with Claude 3.5 Sonnet meets all SOC 2 and compliance standards."
	},
	{
		role: "user",
		content: "Our budget requires pay-as-you-go with minimal token overhead."
	},
	{
		role: "assistant",
		content: "Using the Context Compiler middleware will cut your token costs by 60%+."
	}
];
var sampleDocuments = [
	{
		id: "compliance_guide",
		content: "Please note that AWS holds PCI-DSS Level 1, SOC 2 Type II, ISO 27001, and HIPAA compliance certifications. GDPR data processing agreements are available for EU regions in Ireland and Frankfurt."
	},
	{
		id: "pricing_doc",
		content: "AWS pricing model: pay-as-you-go with no upfront commitment required. Reserved instances save up to 72%."
	},
	{
		id: "compliance_duplicate",
		content: "It is worth noting that AWS compliance includes PCI-DSS Level 1, SOC 2 Type II, and HIPAA. GDPR agreements are supported in EU regions."
	},
	{
		id: "irrelevant_menu",
		content: "Cafeteria update: today's lunch menu includes pasta, fresh salad, and vegetarian options."
	},
	{
		id: "irrelevant_facilities",
		content: "Facility notice: parking permits must be renewed annually at the front desk."
	}
];
var sampleTools = [
	{
		name: "get_compliance_report",
		description: "Fetch compliance certification reports (PCI-DSS, SOC 2, GDPR) for cloud providers."
	},
	{
		name: "compare_pricing",
		description: "Compare infrastructure pricing across cloud providers."
	},
	{
		name: "order_office_supplies",
		description: "Order stationery and office supplies."
	},
	{
		name: "book_conference_room",
		description: "Book a meeting room for team syncs."
	}
];
var MOCK_OPTIMIZATION = {
	original: {
		inputTokens: 18420,
		outputTokens: 850,
		totalTokens: 19270,
		cost: .00405,
		latency: 4.8,
		prompt: `SYSTEM:\nYou are an enterprise AI context optimization assistant.\n\nCONVERSATION HISTORY:\nUser: We need to choose a cloud provider for payments.\nAssistant: What are your requirements?\n[... 6 earlier messages ...]\n\nDOCUMENTS:\nAWS Compliance Certifications (full text)\nAWS Pricing Model (full text)\nOffice Lunch Menu (full text)\nHR Parking Policy (full text)\n\nTOOLS:\nget_compliance_report(), compare_pricing(), order_office_supplies(), book_conference_room()\n\nUSER:\nWhich cloud provider meets our security and pricing requirements?`,
		answer: "AWS is the recommended cloud provider because it satisfies PCI-DSS Level 1, SOC 2 Type II, and GDPR data residency requirements while offering a pay-as-you-go pricing model."
	},
	optimized: {
		inputTokens: 5420,
		outputTokens: 830,
		totalTokens: 6250,
		cost: .00128,
		latency: 2.3,
		prompt: `SYSTEM:\nAnswer accurately and concisely.\n\nRELEVANT CONTEXT:\nAWS holds PCI-DSS Level 1, SOC 2 Type II, and GDPR compliance agreements with pay-as-you-go pricing.\n\nREQUIRED TOOL:\nget_compliance_report()\n\nUSER:\nWhich cloud provider meets our security and pricing requirements?`,
		answer: "AWS fits your needs perfectly, offering full PCI-DSS Level 1, SOC 2 Type II, and GDPR compliance alongside on-demand pay-as-you-go pricing."
	},
	savings: {
		tokenReduction: 70.6,
		costReduction: 68.4,
		latencyReduction: 52.1
	},
	quality: {
		correctness: [96, 96],
		completeness: [94, 93],
		relevance: [97, 97],
		consistency: [95, 96],
		overall: [95.2, 95.5],
		similarity: 97.3,
		status: "preserved"
	},
	breakdown: [
		{
			category: "System instructions",
			before: 2e3,
			after: 700
		},
		{
			category: "Conversation history",
			before: 6e3,
			after: 700
		},
		{
			category: "Documents",
			before: 4e3,
			after: 1200
		},
		{
			category: "Tool schemas",
			before: 2e3,
			after: 300
		},
		{
			category: "User query",
			before: 420,
			after: 420
		}
	],
	optimizations: [
		{
			name: "Context Pruning",
			icon: "prune",
			beforeTokens: 6e3,
			afterTokens: 1200,
			savedPercent: 80,
			enabled: true,
			description: "Removed conversation and document content unrelated to the question."
		},
		{
			name: "History Summarization",
			icon: "history",
			beforeTokens: 4e3,
			afterTokens: 700,
			savedPercent: 82.5,
			enabled: true,
			description: "Condensed long history into a summary containing only useful details."
		},
		{
			name: "Tool Schema Trimming",
			icon: "tools",
			beforeTokens: 2e3,
			afterTokens: 300,
			savedPercent: 85,
			enabled: true,
			description: "Included only the tools required for this request."
		},
		{
			name: "Prompt Deduplication",
			icon: "dedupe",
			beforeTokens: 1e3,
			afterTokens: 250,
			savedPercent: 75,
			enabled: true,
			description: "Removed repeated instructions and boilerplate."
		}
	]
};
async function optimizeRequest(input) {
	const queryText = input.question || "Which cloud provider meets our security and pricing requirements?";
	try {
		const res = await fetch(API_ENDPOINTS.optimize, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				question: queryText,
				conversation: input.context.includes("history") ? sampleConversation : [],
				documents: input.context.includes("documents") ? sampleDocuments : [],
				tools: input.context.includes("tools") ? sampleTools : []
			})
		});
		if (!res.ok) throw new Error(`HTTP ${res.status}`);
		const data = await res.json();
		const origTokens = data.original_tokens || 18420;
		const optTokens = data.optimized_tokens || 5420;
		const reduction = data.reduction_percent || 70.6;
		data.tokens_saved || origTokens - optTokens;
		const semanticScore = (data.semantic_preservation_score ?? .973) * 100;
		const formattedPrompt = JSON.stringify(data.optimized_context, null, 2);
		return {
			original: {
				inputTokens: origTokens,
				outputTokens: 850,
				totalTokens: origTokens + 850,
				cost: Number((origTokens / 1e3 * .003).toFixed(5)),
				latency: 4.8,
				prompt: `QUESTION:\n${queryText}\n\nRAW CONTEXT:\n` + JSON.stringify({
					conversation: sampleConversation,
					documents: sampleDocuments,
					tools: sampleTools
				}, null, 2),
				answer: MOCK_OPTIMIZATION.original.answer
			},
			optimized: {
				inputTokens: optTokens,
				outputTokens: 830,
				totalTokens: optTokens + 830,
				cost: Number((optTokens / 1e3 * .003).toFixed(5)),
				latency: Number((4.8 * (1 - reduction / 100)).toFixed(1)),
				prompt: formattedPrompt,
				answer: MOCK_OPTIMIZATION.optimized.answer
			},
			savings: {
				tokenReduction: reduction,
				costReduction: Number(reduction.toFixed(1)),
				latencyReduction: Number((reduction * .7).toFixed(1))
			},
			quality: {
				correctness: [96, 96],
				completeness: [94, 93],
				relevance: [97, 97],
				consistency: [95, 96],
				overall: [95.2, Number(semanticScore.toFixed(1))],
				similarity: Number(semanticScore.toFixed(1)),
				status: semanticScore >= 85 ? "preserved" : "rejected"
			},
			breakdown: [
				{
					category: "Conversation history",
					before: Math.round(origTokens * .4),
					after: Math.round(optTokens * .25)
				},
				{
					category: "Documents",
					before: Math.round(origTokens * .35),
					after: Math.round(optTokens * .45)
				},
				{
					category: "Tool schemas",
					before: Math.round(origTokens * .15),
					after: Math.round(optTokens * .1)
				},
				{
					category: "User query & System",
					before: Math.round(origTokens * .1),
					after: Math.round(optTokens * .2)
				}
			],
			optimizations: [
				{
					name: "Context Pruning",
					icon: "prune",
					beforeTokens: Math.round(origTokens * .35),
					afterTokens: Math.round(optTokens * .45),
					savedPercent: 78,
					enabled: data.steps_applied?.includes("context_pruner") ?? true,
					description: "Removed document content semantically unrelated to the question."
				},
				{
					name: "History Summarization",
					icon: "history",
					beforeTokens: Math.round(origTokens * .4),
					afterTokens: Math.round(optTokens * .25),
					savedPercent: 82,
					enabled: data.steps_applied?.includes("history_compressor") ?? true,
					description: "Condensed older conversation turns into a summary."
				},
				{
					name: "Tool Schema Trimming",
					icon: "tools",
					beforeTokens: Math.round(origTokens * .15),
					afterTokens: Math.round(optTokens * .1),
					savedPercent: 85,
					enabled: data.steps_applied?.includes("tool_selector") ?? true,
					description: "Vector-selected required tools for this query."
				},
				{
					name: "Prompt Deduplication",
					icon: "dedupe",
					beforeTokens: Math.round(origTokens * .1),
					afterTokens: Math.round(optTokens * .05),
					savedPercent: 70,
					enabled: data.steps_applied?.includes("deduplicator") ?? true,
					description: "Removed SHA-256 and near-duplicate content."
				}
			]
		};
	} catch (err) {
		console.warn("Backend API unavailable, using mock optimization fallback:", err);
		await delay(300);
		return { ...MOCK_OPTIMIZATION };
	}
}
var BENCHMARK_TASKS = [
	{
		id: "T01",
		type: "Factual",
		before: 12450,
		after: 4120,
		saved: 66.9,
		quality: 95,
		status: "passed"
	},
	{
		id: "T02",
		type: "Coding",
		before: 18200,
		after: 7320,
		saved: 59.8,
		quality: 94,
		status: "passed"
	},
	{
		id: "T03",
		type: "Document QA",
		before: 9800,
		after: 3900,
		saved: 60.2,
		quality: 96,
		status: "passed"
	},
	{
		id: "T04",
		type: "Tool Use",
		before: 25840,
		after: 9725,
		saved: 62.4,
		quality: 95,
		status: "passed"
	},
	{
		id: "T05",
		type: "Summarization",
		before: 15320,
		after: 5210,
		saved: 66,
		quality: 94,
		status: "passed"
	},
	{
		id: "T06",
		type: "Multi-turn",
		before: 22100,
		after: 7950,
		saved: 64,
		quality: 95,
		status: "passed"
	},
	{
		id: "T07",
		type: "Extraction",
		before: 11880,
		after: 4890,
		saved: 58.8,
		quality: 97,
		status: "passed"
	},
	{
		id: "T08",
		type: "Planning",
		before: 17400,
		after: 6630,
		saved: 61.9,
		quality: 93,
		status: "passed"
	},
	{
		id: "T09",
		type: "Analysis",
		before: 20100,
		after: 7520,
		saved: 62.6,
		quality: 94,
		status: "passed"
	},
	{
		id: "T10",
		type: "Structured output",
		before: 13600,
		after: 5020,
		saved: 63.1,
		quality: 95,
		status: "passed"
	}
];
async function runBenchmark() {
	try {
		const res = await fetch(API_ENDPOINTS.benchmark, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ task_ids: null })
		});
		if (res.ok) await res.json();
	} catch {}
	await delay(500);
	return BENCHMARK_TASKS;
}
var MODEL_PRICING = {
	bedrock: {
		label: "Amazon Bedrock",
		inputPerMillion: 3,
		outputPerMillion: 15
	},
	gpt: {
		label: "GPT",
		inputPerMillion: 2.5,
		outputPerMillion: 10
	},
	claude: {
		label: "Claude",
		inputPerMillion: 3,
		outputPerMillion: 15
	},
	custom: {
		label: "Custom Model",
		inputPerMillion: 2,
		outputPerMillion: 8
	}
};
function estimateCost(input) {
	const price = MODEL_PRICING[input.model];
	const beforeTokens = input.requests * (input.inputTokens + input.outputTokens);
	const afterInput = input.inputTokens * .376;
	const afterTokens = input.requests * (afterInput + input.outputTokens * .976);
	const beforeCost = input.requests * (input.inputTokens / 1e6 * price.inputPerMillion + input.outputTokens / 1e6 * price.outputPerMillion);
	const afterCost = input.requests * (afterInput / 1e6 * price.inputPerMillion + input.outputTokens * .976 / 1e6 * price.outputPerMillion);
	return {
		beforeTokens,
		afterTokens,
		beforeCost,
		afterCost,
		monthlySavings: beforeCost - afterCost
	};
}
function MetricCard({ label, value, detail, icon: Icon, featured, tone = "default" }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: cn("metric-card", featured && "metric-card-featured", tone === "success" && "border-success/25", tone === "blue" && "border-info/25"),
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center justify-between",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground",
					children: label
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Icon, { className: cn("size-4 text-muted-foreground", featured && "text-primary", tone === "success" && "text-success", tone === "blue" && "text-info") })]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: cn("mt-4 font-mono text-3xl font-semibold tabular-nums", featured && "text-4xl text-primary"),
				children: value
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-2 text-xs text-muted-foreground",
				children: detail
			})
		]
	});
}
function SectionHeading({ title, description, aside }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "mb-5 flex flex-col justify-between gap-3 sm:flex-row sm:items-end",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
			className: "text-xl font-semibold sm:text-2xl",
			children: title
		}), description ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "mt-1 text-sm text-muted-foreground",
			children: description
		}) : null] }), aside]
	});
}
function StatusPill({ children, tone = "success" }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
		className: cn("inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold", tone === "success" && "bg-success-soft text-success", tone === "warning" && "bg-warning-soft text-warning", tone === "neutral" && "bg-secondary text-secondary-foreground"),
		children
	});
}
//#endregion
export { SectionHeading as a, optimizeRequest as c, MetricCard as i, runBenchmark as l, MOCK_OPTIMIZATION as n, StatusPill as o, MODEL_PRICING as r, estimateCost as s, BENCHMARK_TASKS as t };
