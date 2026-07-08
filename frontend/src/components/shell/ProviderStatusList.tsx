"use client";

import { useQuery } from "@tanstack/react-query";
import { CircleDot } from "lucide-react";

import { Skeleton } from "@/components/ui/skeleton";
import { getProviders } from "@/lib/api/ai";
import { cn } from "@/lib/utils";

const STATUS_COLOR: Record<string, string> = {
  UP: "text-success",
  DOWN: "text-danger",
  DEGRADED: "text-warning",
};

export function ProviderStatusList() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["ai-providers"],
    queryFn: getProviders,
    refetchInterval: 30_000,
  });

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[0, 1, 2].map((i) => (
          <Skeleton key={i} className="h-9 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return <p className="text-sm text-muted-foreground">Couldn&apos;t reach the backend.</p>;
  }

  return (
    <ul className="space-y-1">
      {data.map((provider) => (
        <li
          key={provider.name}
          className="flex items-center justify-between rounded-lg px-3 py-2 text-sm hover:bg-surface-2"
        >
          <span className="flex items-center gap-2">
            <CircleDot
              className={cn("size-3.5", STATUS_COLOR[provider.status] ?? "text-muted-foreground")}
            />
            {provider.displayName}
          </span>
          <span className="text-xs text-muted-foreground">
            {provider.configured ? provider.status : "not configured"}
          </span>
        </li>
      ))}
    </ul>
  );
}
