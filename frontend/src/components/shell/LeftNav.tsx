"use client";

import {
  Activity,
  ChevronsLeft,
  ChevronsRight,
  Database,
  MessageSquare,
  Network,
  Plug,
  Sparkles,
  TerminalSquare,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { useCollapsiblePanel } from "@/hooks/useCollapsiblePanel";

import { NavItem } from "./NavItem";

const PRIMARY_NAV = [
  { href: "/", label: "Command Center", icon: Sparkles },
  { href: "/chat", label: "Chat", icon: MessageSquare },
];

const DATABASE_NAV = [
  { href: "/database/connections", label: "Connections", icon: Plug },
  { href: "/database/schema", label: "Schema Explorer", icon: Database },
  { href: "/database/query-studio", label: "SQL Studio", icon: TerminalSquare },
  { href: "/database/er-diagram", label: "ER Diagram", icon: Network },
  { href: "/database/performance", label: "Performance", icon: Activity },
];

export function LeftNav() {
  const { collapsed, toggle } = useCollapsiblePanel("dbpilot:left-nav-collapsed");

  return (
    <nav
      aria-label="Primary"
      className="flex h-full flex-col gap-6 border-r border-border bg-surface-1 p-3 transition-[width] duration-[var(--duration-base)]"
      style={{ width: collapsed ? "4.5rem" : "16rem" }}
    >
      <div className="flex items-center justify-between px-1">
        {!collapsed && <span className="text-sm font-semibold tracking-tight">DBPilot AI</span>}
        <Button
          variant="ghost"
          size="icon"
          className="ml-auto size-8"
          onClick={toggle}
          aria-label={collapsed ? "Expand navigation" : "Collapse navigation"}
        >
          {collapsed ? <ChevronsRight className="size-4" /> : <ChevronsLeft className="size-4" />}
        </Button>
      </div>

      <div className="flex flex-col gap-1">
        {PRIMARY_NAV.map((item) => (
          <NavItem key={item.href} {...item} collapsed={collapsed} />
        ))}
      </div>

      <div className="flex flex-col gap-1">
        {!collapsed && (
          <span className="px-3 pb-1 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Database
          </span>
        )}
        {DATABASE_NAV.map((item) => (
          <NavItem key={item.href} {...item} collapsed={collapsed} />
        ))}
      </div>
    </nav>
  );
}
