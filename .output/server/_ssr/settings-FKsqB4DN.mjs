import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { m as require_jsx_runtime } from "../_libs/@radix-ui/react-collapsible+[...].mjs";
import { T as Check } from "../_libs/lucide-react.mjs";
import { n as Button, r as PageIntro } from "./app-shell-BQIYZ9b5.mjs";
import { t as Input } from "./input-BR4Q3CEJ.mjs";
import { a as SelectValue, i as SelectTrigger, n as SelectContent, r as SelectItem, t as Select } from "./select-DpxQJvzk.mjs";
import { t as Switch } from "./switch-DVo0Penr.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/settings-FKsqB4DN.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function SettingsDashboard() {
	const [saved, setSaved] = (0, import_react.useState)(false);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "page-container py-10 sm:py-14",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PageIntro, {
			eyebrow: "Preferences",
			title: "Settings",
			description: "Set quality safeguards and default context sources for new optimization runs."
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "mt-8 max-w-3xl space-y-4",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
					className: "rounded-lg border border-border bg-card p-5 sm:p-6",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "font-semibold",
						children: "Optimization defaults"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mt-5 grid gap-5 sm:grid-cols-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "mb-1.5 block text-xs font-semibold text-muted-foreground",
							children: "Quality threshold"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "relative",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
								type: "number",
								defaultValue: "90",
								min: "0",
								max: "100",
								className: "pr-8"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "absolute right-3 top-2 text-sm text-muted-foreground",
								children: "%"
							})]
						})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "mb-1.5 block text-xs font-semibold text-muted-foreground",
							children: "Default model"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Select, {
							defaultValue: "bedrock",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectTrigger, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectValue, {}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SelectContent, { children: [
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
						})] })]
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
					className: "rounded-lg border border-border bg-card p-5 sm:p-6",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "font-semibold",
						children: "Default context"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "mt-4 divide-y divide-border",
						children: [
							"Conversation History",
							"Documents",
							"Tool Definitions"
						].map((label) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center justify-between py-4",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-sm",
								children: label
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Switch, {
								defaultChecked: true,
								"aria-label": `Default ${label}`
							})]
						}, label))
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
					onClick: () => {
						setSaved(true);
						window.setTimeout(() => setSaved(false), 1800);
					},
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, {}), saved ? "Settings saved" : "Save Settings"]
				})
			]
		})]
	});
}
var SplitComponent = SettingsDashboard;
//#endregion
export { SplitComponent as component };
