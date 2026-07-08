import { Network } from "lucide-react";

import { LockedFeaturePanel } from "@/components/shared/LockedFeaturePanel";
import { PageHeader } from "@/components/shared/PageHeader";

export default function ErDiagramPage() {
  return (
    <div className="flex h-full flex-col">
      <PageHeader
        title="ER Diagram"
        description="Visualize table relationships across your schema."
      />
      <div className="flex-1 p-6">
        <LockedFeaturePanel
          icon={Network}
          title="No schema to diagram yet"
          description="Connect a database and discover its schema to generate an ER diagram."
          reason="ER diagrams are derived from schema discovery, which hasn't landed yet."
        />
      </div>
    </div>
  );
}
