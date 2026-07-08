import type { ReactNode } from "react";

export function Workspace({ children }: { children: ReactNode }) {
  return (
    <main className="flex min-w-0 flex-1 flex-col overflow-y-auto" id="main-content">
      {children}
    </main>
  );
}
