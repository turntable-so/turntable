import { useEffect, useRef, useState } from "react";
import ChatControls from "./chat-controls";
import ResponseDisplay from "./response-display";
import type { AIMessage } from "./types";

type AiMessageBoxProps = {
  message: AIMessage;
  isLastMessage: boolean;
  isConnected: boolean;
  index: number;
  onEditMessage: (index: number, newContent: string) => void;
  stopWebSocket: () => void;
};

export default function AiMessageBox({
  message,
  isLastMessage,
  isConnected,
  index,
  onEditMessage,
  stopWebSocket,
}: AiMessageBoxProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [input, setInput] = useState(message.content);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onEditMessage(index, input);
    setIsEditing(false);
  };

  useEffect(() => {
    if (isEditing) {
      const handleClickOutside = (event: MouseEvent) => {
        if (
          containerRef.current &&
          !containerRef.current.contains(event.target as Node)
        ) {
          const target = event.target as HTMLElement;
          const isSelectClick =
            target.closest('[role="combobox"]') ||
            target.closest('[role="listbox"]');

          if (!isSelectClick) {
            setIsEditing(false);
          }
        }
      };

      document.addEventListener("mousedown", handleClickOutside);

      return () => {
        document.removeEventListener("mousedown", handleClickOutside);
      };
    }
  }, [isEditing]);

  return (
    <div
      ref={containerRef}
      key={message.id}
      className={`${
        message.role === "user"
          ? "bg-background p-2 rounded-md border border-transparent hover:border-muted-foreground"
          : isLastMessage
            ? "p-1 mb-96"
            : "p-1 mb-8"
      }`}
      onClick={message.role === "user" && !isEditing ? handleEdit : undefined}
    >
      {isEditing ? (
        <ChatControls
          isConnected={isConnected}
          handleSubmit={handleSubmit}
          stopWebSocket={stopWebSocket}
          autoFocus={true}
        />
      ) : message.role === "user" ? (
        <p className="whitespace-pre-wrap">{message.content}</p>
      ) : (
        <ResponseDisplay content={message.content} />
      )}
    </div>
  );
}
