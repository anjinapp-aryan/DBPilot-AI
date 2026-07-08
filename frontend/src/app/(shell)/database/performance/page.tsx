import { Activity } from "lucide-react";

import { LockedFeaturePanel } from "@/components/shared/LockedFeaturePanel";
import { PageHeader } from "@/components/shared/PageHeader";

export default function PerformancePage() {
  return (
    <div className="flex h-full flex-col">
      <PageHeader
        title="Performance Analyzer"
        description="Query metrics and index recommendations."
      />
      <div className="flex-1 p-6">
        <LockedFeaturePanel
          icon={Activity}
          title="No performance data yet"
          description="Connect a database and run some queries to see metrics and index recommendations here."
          reason="Performance analysis depends on query execution, which isn't implemented yet."
        />
      </div>
    </div>
  );
}
