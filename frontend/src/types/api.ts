export interface ApiResponse<T> {
  success: boolean;
  data: T;
  metadata: Record<string, unknown>;
  timestamp: string;
}

export interface ApiErrorBody {
  success: false;
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
  timestamp: string;
}

export interface ChatData {
  response: string;
  provider: string | null;
}

export interface ProviderStatus {
  name: string;
  displayName: string;
  configured: boolean;
  status: string;
  circuitState: string;
  health: string;
}
