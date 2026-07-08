import { ConversationalInput } from "@/components/home/ConversationalInput";
import { Greeting } from "@/components/home/Greeting";
import { PromptChipsSection } from "@/components/home/PromptChipsSection";
import { QuickActions } from "@/components/home/QuickActions";
import { RecentConversations } from "@/components/home/RecentConversations";
import { RecentDatabases } from "@/components/home/RecentDatabases";

export default function HomePage() {
  return (
    <div className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-10 px-6 py-12">
      <Greeting />

      <div className="space-y-4">
        <ConversationalInput />
        <PromptChipsSection />
      </div>

      <QuickActions />

      <div className="grid gap-6 sm:grid-cols-2">
        <RecentDatabases />
        <RecentConversations />
      </div>
    </div>
  );
}
