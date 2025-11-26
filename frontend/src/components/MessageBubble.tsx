import { Message } from "../types.ts";

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble = ({ message }: MessageBubbleProps) => {
  const isUser = message.role === "user";

  return (
    <div
      className="message-row"
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: "0.75rem"
      }}
    >
      <div
        style={{
          maxWidth: "80%",
          padding: "0.8rem 1rem",
          borderRadius: isUser ? "16px 4px 16px 16px" : "4px 16px 16px 16px",
          background: isUser
            ? "linear-gradient(120deg, #3ab0ff, #8360c3)"
            : "rgba(255, 255, 255, 0.08)",
          color: isUser ? "#0b132b" : "#f0f5ff",
          lineHeight: 1.4,
          boxShadow: "0 10px 30px rgba(0,0,0,0.25)",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word"
        }}
      >
        <div
          style={{
            fontSize: "0.75rem",
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            opacity: 0.8,
            marginBottom: "0.3rem"
          }}
        >
          {isUser ? "You" : "Assistant"}
        </div>
        {message.content}
      </div>
    </div>
  );
};

export default MessageBubble;

