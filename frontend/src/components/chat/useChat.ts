"use client";

import { useCallback, useRef, useState } from "react";

import { streamChat } from "@/lib/api/ai";

import type { ChatMessageUI } from "./types";

let idCounter = 0;
function nextId(): string {
  idCounter += 1;
  return `msg-${idCounter}-${Date.now()}`;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessageUI[]>([]);
  const abortRef = useRef<AbortController | null>(null);

  const runAssistantReply = useCallback(async (userText: string, system?: string) => {
    const assistantId = nextId();
    setMessages((prev) => [
      ...prev,
      { id: assistantId, role: "assistant", content: "", streaming: true },
    ]);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      await streamChat(
        { message: userText, system },
        {
          signal: controller.signal,
          onToken: (token) => {
            setMessages((prev) =>
              prev.map((m) => (m.id === assistantId ? { ...m, content: m.content + token } : m)),
            );
          },
          onError: (message) => {
            setMessages((prev) =>
              prev.map((m) => (m.id === assistantId ? { ...m, content: `⚠️ ${message}` } : m)),
            );
          },
        },
      );
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId && !m.content
            ? { ...m, content: "⚠️ Something went wrong reaching the AI Gateway." }
            : m,
        ),
      );
    } finally {
      setMessages((prev) =>
        prev.map((m) => (m.id === assistantId ? { ...m, streaming: false } : m)),
      );
    }
  }, []);

  const sendMessage = useCallback(
    (text: string) => {
      const trimmed = text.trim();
      if (!trimmed) return;
      setMessages((prev) => [...prev, { id: nextId(), role: "user", content: trimmed }]);
      void runAssistantReply(trimmed);
    },
    [runAssistantReply],
  );

  const regenerate = useCallback(
    (messageId: string) => {
      const index = messages.findIndex((m) => m.id === messageId);
      if (index <= 0) return;
      const priorUser = messages[index - 1];
      if (priorUser.role !== "user") return;
      setMessages((prev) => prev.filter((m) => m.id !== messageId));
      void runAssistantReply(priorUser.content);
    },
    [messages, runAssistantReply],
  );

  const explain = useCallback(
    (content: string) => {
      setMessages((prev) => [
        ...prev,
        { id: nextId(), role: "user", content: `Explain this SQL:\n\n${content}` },
      ]);
      void runAssistantReply(content, "Explain the following SQL in plain English, step by step.");
    },
    [runAssistantReply],
  );

  return { messages, sendMessage, regenerate, explain };
}
