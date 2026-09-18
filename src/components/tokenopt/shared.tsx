import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export function MetricCard({ label, value, detail, icon: Icon, featured, tone = "default" }: { label: string; value: string; detail: string; icon: LucideIcon; featured?: boolean; tone?: "default" | "success" | "blue" }) {
  return <div className={cn("metric-card", featured && "metric-card-featured", tone === "success" && "border-success/25", tone === "blue" && "border-info/25")}>
    <div className="flex items-center justify-between"><span className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">{label}</span><Icon className={cn("size-4 text-muted-foreground", featured && "text-primary", tone === "success" && "text-success", tone === "blue" && "text-info")} /></div>
    <div className={cn("mt-4 font-mono text-3xl font-semibold tabular-nums", featured && "text-4xl text-primary")}>{value}</div><p className="mt-2 text-xs text-muted-foreground">{detail}</p>
  </div>;
}

export function SectionHeading({ title, description, aside }: { title: string; description?: string; aside?: React.ReactNode }) {
  return <div className="mb-5 flex flex-col justify-between gap-3 sm:flex-row sm:items-end"><div><h2 className="text-xl font-semibold sm:text-2xl">{title}</h2>{description ? <p className="mt-1 text-sm text-muted-foreground">{description}</p> : null}</div>{aside}</div>;
}

export function StatusPill({ children, tone = "success" }: { children: React.ReactNode; tone?: "success" | "warning" | "neutral" }) {
  return <span className={cn("inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold", tone === "success" && "bg-success-soft text-success", tone === "warning" && "bg-warning-soft text-warning", tone === "neutral" && "bg-secondary text-secondary-foreground")}>{children}</span>;
}
