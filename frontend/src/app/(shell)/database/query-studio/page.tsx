import { TerminalSquare } from "lucide-react";

import { LockedFeaturePanel } from "@/components/shared/LockedFeaturePanel";
import { PageHeader } from "@/components/shared/PageHeader";

export default function QueryStudioPage() {
  return (
    <div className="flex h-full flex-col">
      <PageHeader
        title="SQL Studio"
        description="Write, run, and review SQL against a connected database."
      />
      <div className="flex-1 p-6">
        <LockedFeaturePanel
          icon={TerminalSquare}
          title="SQL execution isn't available yet"
          description="Connect a database to run queries and inspect execution plans here."
          reason="Use the Chat experience to generate SQL today — execution requires a connected database."
        />
      </div>
    </div>
  );
}
