"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useRef } from "react";

import { ChatInput } from "@/components/chat/ChatInput";
import { FollowUpSuggestions } from "@/components/chat/FollowUpSuggestions";
import { MessageList } from "@/components/chat/MessageList";
import { useChat } from "@/components/chat/useChat";

function ChatPageInner() {
  const { messages, sendMessage, regenerate, explain } = useChat();
  const searchParams = useSearchParams();
  const consumedInitialQuery = useRef(false);

  useEffect(() => {
    const initialQuery = searchParams.get("q");
    if (initialQuery && !consumedInitialQuery.current) {
      consumedInitialQuery.current = true;
      sendMessage(initialQuery);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const lastMessage = messages[messages.length - 1];
  const showFollowUps =
    lastMessage?.role === "assistant" && !lastMessage.streaming && lastMessage.content;

  return (
    <div className="flex h-full flex-col">
      {messages.length === 0 ? (
        <div className="flex flex-1 items-center justify-center px-6 text-center text-muted-foreground">
          <p>Start a conversation about your database.</p>
        </div>
      ) : (
        <MessageList messages={messages} onRegenerate={regenerate} onExplain={explain} />
      )}
      {showFollowUps && <FollowUpSuggestions onSelect={sendMessage} />}
      <ChatInput onSend={sendMessage} />
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={null}>
      <ChatPageInner />
    </Suspense>
  );
}
