"use client";

import { ArrowUp } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { VoiceButton } from "@/components/voice/VoiceButton";

export function ConversationalInput() {
  const [value, setValue] = useState("");
  const router = useRouter();

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed) return;
    router.push(`/chat?q=${encodeURIComponent(trimmed)}`);
  };

  return (
    <div className="glass flex flex-col gap-3 rounded-2xl p-4">
      <Textarea
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            submit();
          }
        }}
        placeholder="Ask anything about your database…"
        rows={3}
        className="resize-none border-none bg-transparent p-2 text-base shadow-none focus-visible:ring-0"
        aria-label="Message DBPilot AI"
      />
      <div className="flex items-center justify-between">
        <VoiceButton onTranscript={(text) => setValue(text)} />
        <Button
          type="button"
          size="icon"
          className="size-10 rounded-full"
          disabled={!value.trim()}
          onClick={submit}
          aria-label="Send message"
        >
          <ArrowUp className="size-5" />
        </Button>
      </div>
    </div>
  );
}
