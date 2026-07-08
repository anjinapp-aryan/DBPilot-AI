"use client";

const PROMPTS = [
  "What can you help me with?",
  "Explain how schema discovery will work",
  "Write a SQL query to find duplicate rows",
  "What's the AI Gateway's failover order?",
];

export function PromptChips({ onSelect }: { onSelect: (prompt: string) => void }) {
  return (
    <div className="flex flex-wrap gap-2" role="list" aria-label="Suggested prompts">
      {PROMPTS.map((prompt) => (
        <button
          key={prompt}
          type="button"
          role="listitem"
          onClick={() => onSelect(prompt)}
          className="rounded-full border border-border bg-surface-1 px-4 py-2 text-sm text-muted-foreground transition-colors duration-[var(--duration-fast)] hover:border-accent/40 hover:bg-surface-2 hover:text-foreground"
        >
          {prompt}
        </button>
      ))}
    </div>
  );
}
