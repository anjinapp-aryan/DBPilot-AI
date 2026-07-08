"use client";

import { Clock, Database, Sparkles } from "lucide-react";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LockedFeaturePanel } from "@/components/shared/LockedFeaturePanel";

import { ProviderStatusList } from "./ProviderStatusList";

export function RightPanelContent() {
  return (
    <Tabs defaultValue="context" className="flex h-full flex-col">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="context">Context</TabsTrigger>
        <TabsTrigger value="metadata">Metadata</TabsTrigger>
        <TabsTrigger value="history">History</TabsTrigger>
      </TabsList>

      <TabsContent value="context" className="mt-4 flex-1 overflow-y-auto">
        <h3 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          <Sparkles className="size-3.5" /> AI Gateway
        </h3>
        <ProviderStatusList />
      </TabsContent>

      <TabsContent value="metadata" className="mt-4 flex-1">
        <LockedFeaturePanel
          title="No database metadata"
          description="Connect a database to see live schema metadata here."
          icon={Database}
        />
      </TabsContent>

      <TabsContent value="history" className="mt-4 flex-1">
        <LockedFeaturePanel
          title="No execution history"
          description="Query history isn't available yet."
          icon={Clock}
        />
      </TabsContent>
    </Tabs>
  );
}

export function RightPanel() {
  return (
    <aside
      className="glass hidden h-full w-80 shrink-0 flex-col rounded-tl-2xl p-4 xl:flex"
      aria-label="Context"
    >
      <RightPanelContent />
    </aside>
  );
}
