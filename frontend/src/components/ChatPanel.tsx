import { FormEvent, useRef, useState } from "react";
import MessageBubble from "./MessageBubble.tsx";
import { Message } from "../types.ts";

interface ChatPanelProps {
  messages: Message[];
  onSend: (text: string) => Promise<void> | void;
  loading: boolean;
  error: string | null;
}

const ChatPanel = ({ messages, onSend, loading, error }: ChatPanelProps) => {
  const [draft, setDraft] = useState("");
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = draft.trim();
    if (!trimmed) return;
    setDraft("");
    await onSend(trimmed);
    inputRef.current?.focus();
  };

  return (
    <div className="chat-panel">
      <header className="chat-panel__header">
        <div>
          <p className="eyebrow">ID2223 Assistant</p>
          <h1>Educational Stock Chatbot</h1>
          <p className="subtitle">
            Ask about companies, ratios, or investing theory. Responses are for
            learning only.
          </p>
        </div>
        <div className="pill">{loading ? "Thinking…" : "Ready"}</div>
      </header>

      <section className="chat-panel__history">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {messages.length === 0 && (
          <div className="empty-state">
            <p>Try asking: “Compare Tesla and Ford long-term outlook.”</p>
          </div>
        )}
      </section>

      {error && <div className="error-banner">{error}</div>}

      <form className="chat-panel__composer" onSubmit={handleSubmit}>
        <textarea
          ref={inputRef}
          rows={3}
          placeholder="Ask anything about stocks or financial concepts…"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Sending…" : "Send"}
        </button>
      </form>
    </div>
  );
};

export default ChatPanel;

