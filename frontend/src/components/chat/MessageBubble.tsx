import { motion } from "motion/react";

import { cn } from "@/lib/utils";

import { MessageActionBar } from "./MessageActionBar";
import { StreamingText } from "./StreamingText";
import type { ChatMessageUI } from "./types";

export interface MessageBubbleProps {
  message: ChatMessageUI;
  onRegenerate: (messageId: string) => void;
  onExplain: (content: string) => void;
}

export function MessageBubble({ message, onRegenerate, onExplain }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
      className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-3 text-sm",
          isUser ? "bg-accent-muted text-foreground" : "bg-surface-1 text-foreground",
        )}
      >
        <StreamingText content={message.content} streaming={Boolean(message.streaming)} />
        {!isUser && message.content && !message.streaming && (
          <MessageActionBar
            content={message.content}
            onRegenerate={() => onRegenerate(message.id)}
            onExplain={() => onExplain(message.content)}
          />
        )}
        {!isUser && message.provider && (
          <p className="mt-1 text-[0.7rem] text-muted-foreground/70">via {message.provider}</p>
        )}
      </div>
    </motion.div>
  );
}
