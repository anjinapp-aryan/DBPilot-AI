const SUGGESTIONS = [
  "Can you explain that further?",
  "Show me an example query",
  "What should I try next?",
];

export function FollowUpSuggestions({ onSelect }: { onSelect: (text: string) => void }) {
  return (
    <div className="flex flex-wrap gap-2 px-6 pb-2" role="list" aria-label="Follow-up suggestions">
      {SUGGESTIONS.map((s) => (
        <button
          key={s}
          type="button"
          role="listitem"
          onClick={() => onSelect(s)}
          className="rounded-full border border-border bg-surface-1 px-3 py-1.5 text-xs text-muted-foreground transition-colors duration-[var(--duration-fast)] hover:border-accent/40 hover:text-foreground"
        >
          {s}
        </button>
      ))}
    </div>
  );
}
