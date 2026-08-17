import { apiFetch } from "./client";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  message: string;
  conversation_id: string;
  caller_phone_number: string;
}

export interface ChatResponse {
  reply: string;
}

// Stable per-browser-session id so the backend can track conversation
// history across messages without a real login system.
function getConversationId(): string {
  if (typeof window === "undefined") return "server-session";
  const key = "medivoice_conversation_id";
  let id = window.sessionStorage.getItem(key);
  if (!id) {
    id = `web-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    window.sessionStorage.setItem(key, id);
  }
  return id;
}

/** POST /chat */
export async function sendChatMessage(message: string): Promise<string> {
  const payload: ChatRequest = {
    message,
    conversation_id: getConversationId(),
    caller_phone_number: "web-dashboard",
  };

  const data = await apiFetch<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  return data.reply;
}
