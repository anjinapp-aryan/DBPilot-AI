import { MarkdownRenderer } from "./MarkdownRenderer";

export interface StreamingTextProps {
  content: string;
  streaming: boolean;
}

/**
 * Renders message content as markdown. `streaming` just toggles the
 * trailing cursor — token accumulation itself happens in useChat, so this
 * component doesn't care whether tokens arrived via real SSE or a single
 * non-streaming response.
 */
export function StreamingText({ content, streaming }: StreamingTextProps) {
  return (
    <div className="relative">
      <MarkdownRenderer content={content} />
      {streaming && (
        <span
          className="ml-0.5 inline-block h-4 w-1.5 animate-pulse bg-accent align-middle"
          aria-hidden="true"
        />
      )}
    </div>
  );
}
