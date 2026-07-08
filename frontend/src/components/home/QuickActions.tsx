"use client";

import { Activity, Database, Network, Plug, TerminalSquare } from "lucide-react";
import { motion } from "motion/react";
import Link from "next/link";

import { Card } from "@/components/ui/card";

const ACTIONS = [
  { href: "/database/connections", label: "Connect Database", icon: Plug },
  { href: "/database/schema", label: "Schema Explorer", icon: Database },
  { href: "/database/query-studio", label: "SQL Studio", icon: TerminalSquare },
  { href: "/database/er-diagram", label: "ER Diagram", icon: Network },
  { href: "/database/performance", label: "Performance Analyzer", icon: Activity },
];

export function QuickActions() {
  return (
    <section aria-labelledby="quick-actions-heading" className="space-y-3">
      <h2 id="quick-actions-heading" className="text-sm font-semibold text-foreground">
        Quick actions
      </h2>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        {ACTIONS.map(({ href, label, icon: Icon }) => (
          <Link key={href} href={href}>
            <motion.div
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.97 }}
              transition={{ duration: 0.15 }}
            >
              <Card className="flex flex-col items-center gap-2 rounded-xl p-4 text-center transition-colors duration-[var(--duration-fast)] hover:border-accent/40 hover:bg-surface-2">
                <Icon className="size-5 text-accent" aria-hidden="true" />
                <span className="text-xs font-medium text-foreground">{label}</span>
              </Card>
            </motion.div>
          </Link>
        ))}
      </div>
    </section>
  );
}
