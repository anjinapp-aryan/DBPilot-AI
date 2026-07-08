import { ConnectionList } from "@/components/database/connections/ConnectionList";
import { NewConnectionDialog } from "@/components/database/connections/NewConnectionDialog";
import { PageHeader } from "@/components/shared/PageHeader";

export default function ConnectionsPage() {
  return (
    <div className="flex h-full flex-col">
      <PageHeader
        title="Connections"
        description="Manage the databases DBPilot AI can talk to."
        actions={<NewConnectionDialog />}
      />
      <div className="flex-1 p-6">
        <ConnectionList />
      </div>
    </div>
  );
}
