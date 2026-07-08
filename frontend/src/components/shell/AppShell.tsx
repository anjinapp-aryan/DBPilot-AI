import type { ReactNode } from "react";

import { LeftNav } from "./LeftNav";
import { MobileTopBar } from "./MobileTopBar";
import { RightPanel } from "./RightPanel";
import { Workspace } from "./Workspace";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-dvh flex-col overflow-hidden bg-background">
      <MobileTopBar />
      <div className="flex min-h-0 flex-1">
        <div className="hidden xl:block">
          <LeftNav />
        </div>
        <Workspace>{children}</Workspace>
        <RightPanel />
      </div>
    </div>
  );
}
