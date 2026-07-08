"use client";

import { ArrowUp } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { VoiceButton } from "@/components/voice/VoiceButton";

export interface ChatInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed) return;
    onSend(trimmed);
    setValue("");
  };

  return (
    <div className="border-t border-border bg-surface-0 p-4">
      <div className="glass mx-auto flex max-w-3xl items-end gap-2 rounded-2xl p-3">
        <Textarea
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              submit();
            }
          }}
          placeholder="Message DBPilot AI…"
          rows={1}
          disabled={disabled}
          className="max-h-40 resize-none border-none bg-transparent p-2 text-sm shadow-none focus-visible:ring-0"
          aria-label="Message DBPilot AI"
        />
        <VoiceButton onTranscript={(text) => setValue(text)} />
        <Button
          type="button"
          size="icon"
          className="size-9 shrink-0 rounded-full"
          disabled={disabled || !value.trim()}
          onClick={submit}
          aria-label="Send message"
        >
          <ArrowUp className="size-4.5" />
        </Button>
      </div>
    </div>
  );
}
