"use client";

import {
  Check,
  Copy,
  Download,
  LineChart,
  type LucideIcon,
  Play,
  RotateCw,
  Save,
  Sparkles,
} from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

interface ActionButtonProps {
  label: string;
  icon: LucideIcon;
  onClick?: () => void;
  disabledReason?: string;
}

function ActionButton({ label, icon: Icon, onClick, disabledReason }: ActionButtonProps) {
  const button = (
    <Button
      variant="ghost"
      size="sm"
      className="h-7 gap-1.5 px-2 text-xs text-muted-foreground hover:text-foreground"
      disabled={Boolean(disabledReason)}
      aria-disabled={Boolean(disabledReason)}
      onClick={onClick}
    >
      <Icon className="size-3.5" />
      {label}
    </Button>
  );

  if (!disabledReason) return button;

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span tabIndex={0}>{button}</span>
      </TooltipTrigger>
      <TooltipContent>{disabledReason}</TooltipContent>
    </Tooltip>
  );
}

export interface MessageActionBarProps {
  content: string;
  onRegenerate: () => void;
  onExplain: () => void;
}

export function MessageActionBar({ content, onRegenerate, onExplain }: MessageActionBarProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="flex flex-wrap items-center gap-0.5 pt-1">
      <ActionButton
        label={copied ? "Copied" : "Copy"}
        icon={copied ? Check : Copy}
        onClick={handleCopy}
      />
      <ActionButton label="Regenerate" icon={RotateCw} onClick={onRegenerate} />
      <ActionButton label="Explain" icon={Sparkles} onClick={onExplain} />
      <ActionButton
        label="Execute"
        icon={Play}
        disabledReason="Connect a database to execute SQL — coming in a later phase."
      />
      <ActionButton label="Save" icon={Save} disabledReason="Query history isn't available yet." />
      <ActionButton
        label="Visualize"
        icon={LineChart}
        disabledReason="Visualization needs query results — connect a database first."
      />
      <ActionButton
        label="Export"
        icon={Download}
        disabledReason="Nothing to export until a database is connected."
      />
    </div>
  );
}
