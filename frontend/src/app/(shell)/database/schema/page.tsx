import { Database } from "lucide-react";

import { LockedFeaturePanel } from "@/components/shared/LockedFeaturePanel";
import { PageHeader } from "@/components/shared/PageHeader";

export default function SchemaExplorerPage() {
  return (
    <div className="flex h-full flex-col">
      <PageHeader
        title="Schema Explorer"
        description="Browse tables, columns, and relationships."
      />
      <div className="flex-1 p-6">
        <LockedFeaturePanel
          icon={Database}
          title="Schema discovery isn't available yet"
          description="Connect a database to explore its schema here."
          reason="The backend's schema discovery service is a Phase 2 stub today."
        />
      </div>
    </div>
  );
}
