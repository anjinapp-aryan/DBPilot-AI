import { Database } from "lucide-react";

import { EmptyState } from "@/components/shared/EmptyState";

export function RecentDatabases() {
  return (
    <section aria-labelledby="recent-databases-heading" className="space-y-3">
      <h2 id="recent-databases-heading" className="text-sm font-semibold text-foreground">
        Recently connected databases
      </h2>
      <EmptyState
        icon={Database}
        title="No databases connected yet"
        description="Connect a database to see it here."
      />
    </section>
  );
}
