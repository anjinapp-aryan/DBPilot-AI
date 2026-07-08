import type { LucideIcon } from "lucide-react";

export interface EmptyStateProps {
  title: string;
  description: string;
  icon: LucideIcon;
}

/** Compact inline empty state for cards/tiles (vs. the full-page LockedFeaturePanel). */
export function EmptyState({ title, description, icon: Icon }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-border p-6 text-center">
      <Icon className="size-5 text-muted-foreground" aria-hidden="true" />
      <p className="text-sm font-medium text-foreground">{title}</p>
      <p className="text-xs text-muted-foreground">{description}</p>
    </div>
  );
}
