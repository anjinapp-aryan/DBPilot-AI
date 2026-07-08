import type { ApiErrorBody, ApiResponse } from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  code: string;

  constructor(message: string, code: string) {
    super(message);
    this.name = "ApiError";
    this.code = code;
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  const body = (await res.json()) as ApiResponse<T> | ApiErrorBody;

  if (!res.ok || body.success === false) {
    const errorBody = body as ApiErrorBody;
    throw new ApiError(
      errorBody.error?.message ?? "Request failed",
      errorBody.error?.code ?? "unknown_error",
    );
  }

  return (body as ApiResponse<T>).data;
}

export { API_BASE_URL };
