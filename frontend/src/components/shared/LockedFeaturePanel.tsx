import type { LucideIcon } from "lucide-react";

import { Button } from "@/components/ui/button";

export interface LockedFeaturePanelProps {
  title: string;
  description: string;
  icon: LucideIcon;
  reason?: string;
  cta?: { label: string; onClick: () => void };
}

/**
 * The honest empty state for any screen without real backend support yet.
 * Never populated with fabricated/sample data — this component IS the
 * content until the backing feature ships.
 */
export function LockedFeaturePanel({
  title,
  description,
  icon: Icon,
  reason,
  cta,
}: LockedFeaturePanelProps) {
  return (
    <div className="flex h-full min-h-[24rem] flex-col items-center justify-center gap-4 rounded-xl border border-dashed border-border bg-surface-1/40 p-12 text-center">
      <div className="flex size-14 items-center justify-center rounded-full bg-accent-muted text-accent">
        <Icon className="size-7" aria-hidden="true" />
      </div>
      <div className="space-y-1.5">
        <h2 className="text-lg font-semibold text-foreground">{title}</h2>
        <p className="max-w-sm text-sm text-muted-foreground">{description}</p>
      </div>
      {reason ? <p className="max-w-sm text-xs text-muted-foreground/80">{reason}</p> : null}
      {cta ? (
        <Button variant="secondary" size="sm" onClick={cta.onClick}>
          {cta.label}
        </Button>
      ) : null}
    </div>
  );
}
