import { Link, useRouterState } from "@tanstack/react-router";
import { BarChart3, Bolt, Gauge, Menu, Settings, X } from "lucide-react";
import { useState, type ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const nav = [
  { to: "/", label: "Optimize", icon: Bolt },
  { to: "/benchmarks", label: "Benchmarks", icon: Gauge },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/settings", label: "Settings", icon: Settings },
] as const;

export function AppShell({ children }: { children: ReactNode }) {
  const path = useRouterState({ select: (s) => s.location.pathname });
  const [open, setOpen] = useState(false);
  return <div className="min-h-screen bg-background">
    <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-[1440px] items-center gap-8 px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex shrink-0 items-center gap-3" aria-label="TokenOpt home">
          <span className="flex size-8 items-center justify-center rounded-md bg-primary text-primary-foreground"><Bolt className="size-4 fill-current" /></span>
          <span><span className="block font-display text-lg font-bold leading-none">TokenOpt</span><span className="mt-1 hidden text-[10px] font-medium uppercase tracking-[0.14em] text-muted-foreground sm:block">LLM Token Optimization Engine</span></span>
        </Link>
        <nav className="ml-auto hidden items-center gap-1 md:flex" aria-label="Main navigation">
          {nav.map((item) => { const active = item.to === "/" ? path === "/" : path.startsWith(item.to); return <Button key={item.to} variant="ghost" size="sm" asChild className={cn("text-muted-foreground", active && "bg-secondary text-foreground")}><Link to={item.to}><item.icon className="size-4" />{item.label}</Link></Button>; })}
        </nav>
        <Button variant="outline" size="icon" className="ml-auto md:hidden" onClick={() => setOpen((v) => !v)} aria-label="Toggle navigation">{open ? <X /> : <Menu />}</Button>
      </div>
      {open ? <nav className="grid gap-1 border-t border-border p-3 md:hidden">{nav.map((item) => <Button key={item.to} variant="ghost" asChild className="justify-start" onClick={() => setOpen(false)}><Link to={item.to}><item.icon />{item.label}</Link></Button>)}</nav> : null}
    </header>
    {children}
  </div>;
}

export function PageIntro({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: ReactNode }) {
  return <div className="flex flex-col justify-between gap-5 border-b border-border pb-7 sm:flex-row sm:items-end"><div><p className="eyebrow">{eyebrow}</p><h1 className="mt-2 max-w-3xl text-3xl font-bold text-foreground sm:text-4xl">{title}</h1><p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground sm:text-base">{description}</p></div>{action}</div>;
}
