import { useCallback, useState } from "react";
import ChatPanel from "./components/ChatPanel";
import type { Message } from "./types";

// For deployment we hard-code the KTH Cloud backend URL so the frontend
// always talks to the correct API even when built inside Docker.
const API_URL = "https://id2223-chatbot.app.cloud.cbh.kth.se/chat";

const createId = () => {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

const buildMessage = (role: Message["role"], content: string): Message => ({
  id: createId(),
  role,
  content,
  timestamp: new Date().toISOString()
});

const App = () => {
  const [messages, setMessages] = useState<Message[]>([
    buildMessage(
      "assistant",
      "Hi! I'm your assistant. Ask me about anything you need help with and I will try to help out."
    )
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (text: string) => {
      const userMessage = buildMessage("user", text);
      const nextHistory = [...messages, userMessage];
      setMessages(nextHistory);
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: text,
            history: nextHistory
          })
        });

        if (!response.ok) {
          throw new Error(`Backend error ${response.status}`);
        }

        const data = await response.json();
        const reply =
          data?.answer ??
          "I had trouble parsing that response, but I'm here to help!";

        setMessages((prev) => [...prev, buildMessage("assistant", reply)]);
      } catch (err) {
        console.error(err);
        setError("Unable to reach the backend. Showing an offline response.");
        setMessages((prev) => [
          ...prev,
          buildMessage(
            "assistant",
            "I'm offline right now, but you can still explore investment questions!"
          )
        ]);
      } finally {
        setLoading(false);
      }
    },
    [messages]
  );

  return (
    <main className="app-shell">
      <ChatPanel
        messages={messages}
        onSend={sendMessage}
        loading={loading}
        error={error}
      />
    </main>
  );
};

export default App;

