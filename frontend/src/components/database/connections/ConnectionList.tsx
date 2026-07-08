import { Plug } from "lucide-react";

import { LockedFeaturePanel } from "@/components/shared/LockedFeaturePanel";

export function ConnectionList() {
  return (
    <LockedFeaturePanel
      icon={Plug}
      title="No connections yet"
      description="Add a database connection to start exploring schema, running queries, and chatting with your data."
      reason="Connection management lands in a later backend phase — the form below is a preview."
    />
  );
}
