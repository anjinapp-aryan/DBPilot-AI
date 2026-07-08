import { MessageSquare } from "lucide-react";

import { EmptyState } from "@/components/shared/EmptyState";

export function RecentConversations() {
  return (
    <section aria-labelledby="recent-conversations-heading" className="space-y-3">
      <h2 id="recent-conversations-heading" className="text-sm font-semibold text-foreground">
        Recent conversations
      </h2>
      <EmptyState
        icon={MessageSquare}
        title="No saved conversations yet"
        description="Conversation history isn't available yet."
      />
    </section>
  );
}
