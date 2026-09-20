import { createFileRoute } from "@tanstack/react-router";
import { OptimizeDashboard } from "@/components/tokenopt/optimize-dashboard";

export const Route = createFileRoute("/")({
  head: () => ({ meta: [
    { title: "Optimize LLM Tokens — TokenOpt" },
    { name: "description", content: "Analyze LLM requests, reduce context and cost, and verify answer quality with TokenOpt." },
    { property: "og:title", content: "Optimize LLM Tokens — TokenOpt" },
    { property: "og:description", content: "Reduce LLM input tokens while preserving answer quality." },
    { property: "og:type", content: "website" },
    { name: "twitter:card", content: "summary_large_image" },
  ]}),
  component: OptimizeDashboard,
});
