"use client";

import { Check, Copy } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { highlightCode } from "@/lib/highlight";

export interface SqlCodeBlockProps {
  code: string;
  language: string;
}

export function SqlCodeBlock({ code, language }: SqlCodeBlockProps) {
  const [html, setHtml] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let cancelled = false;
    highlightCode(code, language).then((result) => {
      if (!cancelled) setHtml(result);
    });
    return () => {
      cancelled = true;
    };
  }, [code, language]);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="group relative my-3 overflow-hidden rounded-xl border border-border bg-[#0d1117]">
      <div className="flex items-center justify-between border-b border-border/60 px-4 py-1.5">
        <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {language}
        </span>
        <Button
          variant="ghost"
          size="icon"
          className="size-7"
          onClick={handleCopy}
          aria-label="Copy code"
        >
          {copied ? <Check className="size-3.5 text-success" /> : <Copy className="size-3.5" />}
        </Button>
      </div>
      {html ? (
        <div
          className="overflow-x-auto text-sm [&>pre]:p-4"
          dangerouslySetInnerHTML={{ __html: html }}
        />
      ) : (
        <pre className="overflow-x-auto p-4 text-sm text-foreground">
          <code>{code}</code>
        </pre>
      )}
    </div>
  );
}
