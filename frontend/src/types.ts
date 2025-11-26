export type Role = "user" | "assistant";

export interface Message {
  id: string;
  role: Role;
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  answer?: string;
  history?: Message[];
}

