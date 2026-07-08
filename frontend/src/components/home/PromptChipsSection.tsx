"use client";

import { useRouter } from "next/navigation";

import { PromptChips } from "./PromptChips";

export function PromptChipsSection() {
  const router = useRouter();

  return (
    <PromptChips onSelect={(prompt) => router.push(`/chat?q=${encodeURIComponent(prompt)}`)} />
  );
}
