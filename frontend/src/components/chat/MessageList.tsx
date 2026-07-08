"use client";

import { useEffect, useRef } from "react";

import { MessageBubble } from "./MessageBubble";
import type { ChatMessageUI } from "./types";

export interface MessageListProps {
  messages: ChatMessageUI[];
  onRegenerate: (messageId: string) => void;
  onExplain: (content: string) => void;
}

export function MessageList({ messages, onRegenerate, onExplain }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-1 flex-col gap-4 overflow-y-auto px-6 py-6">
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
          onRegenerate={onRegenerate}
          onExplain={onExplain}
        />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
