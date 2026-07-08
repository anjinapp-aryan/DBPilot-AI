import { API_BASE_URL, apiFetch } from "@/lib/api/client";
import type { ChatData, ProviderStatus } from "@/types/api";

export interface ChatRequest {
  message: string;
  system?: string;
}

export function postChat(payload: ChatRequest): Promise<ChatData> {
  return apiFetch<ChatData>("/api/v1/ai/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getProviders(): Promise<ProviderStatus[]> {
  return apiFetch<ProviderStatus[]>("/api/v1/ai/providers");
}

export interface StreamChatHandlers {
  onToken: (token: string) => void;
  onError?: (message: string) => void;
  signal?: AbortSignal;
}

/**
 * Consumes POST /api/v1/ai/chat/stream (SSE-over-fetch, not EventSource,
 * since this is a POST with a body). Falls back to the non-streaming
 * /chat endpoint if the server returns a non-OK response (e.g. the route
 * isn't deployed yet), so callers get a single onToken call with the
 * full response rather than silently failing.
 */
export async function streamChat(
  payload: ChatRequest,
  handlers: StreamChatHandlers,
): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/v1/ai/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal: handlers.signal,
  });

  if (!res.ok || !res.body) {
    const data = await postChat(payload);
    handlers.onToken(data.response);
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";

    for (const frame of frames) {
      if (frame.startsWith("event: error")) {
        const dataLine = frame.split("\n").find((l) => l.startsWith("data: "));
        const message = dataLine ? JSON.parse(dataLine.slice(6)).message : "Stream error";
        handlers.onError?.(message);
        continue;
      }
      const dataLine = frame.split("\n").find((l) => l.startsWith("data: "));
      if (!dataLine) continue;
      const raw = dataLine.slice(6);
      if (raw === "[DONE]") continue;
      const parsed = JSON.parse(raw) as { token: string };
      handlers.onToken(parsed.token);
    }
  }
}
