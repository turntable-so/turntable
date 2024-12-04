import type { FileNode, OpenedFile } from "@/app/contexts/FilesContext";
import type { Lineage } from "@/app/contexts/LineageView";
import type { Dispatch, SetStateAction } from "react";
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
  aiActiveFile: OpenedFile | null;
  setAiActiveFile: Dispatch<SetStateAction<OpenedFile | null>>;
  aiLineageContext: Lineage | null;
  setAiLineageContext: Dispatch<SetStateAction<Lineage | null>>;
  contextFiles: FileNode[];
  setContextFiles: Dispatch<SetStateAction<FileNode[]>>;
  selectedModel: string;
  setSelectedModel: Dispatch<SetStateAction<string>>;
};

export default function AiMessageBox({
  message,
  isLastMessage,
  isConnected,
  index,
  onEditMessage,
  aiActiveFile,
  setAiActiveFile,
  aiLineageContext,
  setAiLineageContext,
  contextFiles,
  setContextFiles,
  selectedModel,
  setSelectedModel,
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
          const isSelectClick = target.closest('[role="combobox"]') || 
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
          input={input}
          setInput={setInput}
          isLoading={false}
          isConnected={isConnected}
          handleSubmit={handleSubmit}
          aiActiveFile={aiActiveFile}
          setAiActiveFile={setAiActiveFile}
          aiLineageContext={aiLineageContext}
          setAiLineageContext={setAiLineageContext}
          contextFiles={contextFiles}
          setContextFiles={setContextFiles}
          selectedModel={selectedModel}
          setSelectedModel={setSelectedModel}
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