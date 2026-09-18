# TokenOpt Dashboard

## Overview
Rebuild the current single-screen benchmark into a polished, frontend-only TokenOpt product. Keep the project’s TanStack Start foundation (the supported equivalent of the requested Next.js setup), with React, TypeScript, Tailwind, shadcn/ui, Lucide, and Recharts.

## Optimize page
- Add a compact product header with TokenOpt identity and navigation.
- Build the question-first optimization workspace with model selection, context toggles, example loading, and a prominent Analyze & Optimize action.
- Implement a timed analysis sequence with progressive completion states, then automatically reveal results.
- Present results in the requested visual order: dominant token reduction, supporting KPIs, before/after comparison, removed context, quality verification, answer comparison, then detailed charts.
- Add interactive prompt tabs, copy action with confirmation, technique enable/disable controls, and expandable strategy rationale.
- Include a rejected-quality variant in the data model and display logic when results fall below the configured threshold.

## Benchmarks page
- Create a dedicated fixed-workload benchmark view with summary metrics, task table, statuses, and an interactive Run Benchmark state.
- Preserve the existing 10-task workload concept while presenting realistic mock benchmark results for a predictable demo.

## Analytics page
- Create a configurable cost simulator with monthly requests, token volumes, and model choice.
- Calculate before/after monthly and yearly costs from a separate configurable pricing model.
- Add request-versus-cost, token comparison, and quality-versus-token Pareto charts.

## Settings page
- Add a focused settings view for quality threshold, default model, and default context sources so every navigation destination is functional.

## Shared structure and data
- Create a reusable application shell, shared dashboard components, typed mock response models, and a separate service layer shaped for future `/api/optimize`, `/api/evaluate`, `/api/benchmark`, `/api/analytics`, and `/api/cost-estimate` calls.
- Keep all current behavior local and deterministic; no database or external service is required.
- Refresh the visual system with a crisp light infrastructure aesthetic, strong green savings signals, restrained blue accents, compact geometry, and responsive layouts.
- Add unique metadata for every page.

## Validation
- Verify loading, example, copy, toggles, benchmark run, simulator calculations, and navigation.
- Check desktop and mobile layouts, especially tables, charts, prompt panels, and the before/after comparison.
- Confirm the final preview builds without errors.
