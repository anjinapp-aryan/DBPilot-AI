export interface ChatMessageUI {
  id: string;
  role: "user" | "assistant";
  content: string;
  provider?: string | null;
  streaming?: boolean;
}
