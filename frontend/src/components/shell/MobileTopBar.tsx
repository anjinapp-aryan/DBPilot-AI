"use client";

import { PanelLeft, PanelRight } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet";
import { LeftNav } from "./LeftNav";
import { RightPanelContent } from "./RightPanel";

export function MobileTopBar() {
  const [navOpen, setNavOpen] = useState(false);
  const [contextOpen, setContextOpen] = useState(false);

  return (
    <div className="flex items-center justify-between border-b border-border bg-surface-1 px-3 py-2 xl:hidden">
      <Button
        variant="ghost"
        size="icon"
        aria-label="Open navigation"
        onClick={() => setNavOpen(true)}
      >
        <PanelLeft className="size-5" />
      </Button>
      <span className="text-sm font-semibold tracking-tight">DBPilot AI</span>
      <Button
        variant="ghost"
        size="icon"
        aria-label="Open context panel"
        onClick={() => setContextOpen(true)}
      >
        <PanelRight className="size-5" />
      </Button>

      <Sheet open={navOpen} onOpenChange={setNavOpen}>
        <SheetContent side="left" className="w-72 p-0">
          <SheetTitle className="sr-only">Navigation</SheetTitle>
          <LeftNav />
        </SheetContent>
      </Sheet>

      <Sheet open={contextOpen} onOpenChange={setContextOpen}>
        <SheetContent side="right" className="w-80 p-0">
          <SheetTitle className="sr-only">Context</SheetTitle>
          <div className="flex h-full flex-col p-4">
            <RightPanelContent />
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}
