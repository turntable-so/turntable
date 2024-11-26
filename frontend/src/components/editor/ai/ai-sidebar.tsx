import { LocalStorageKeys } from "@/app/constants/local-storage-keys";
import { type FileNode, useFiles } from "@/app/contexts/FilesContext";
import { useWebSocket } from "@/app/hooks/use-websocket";
import getUrl from "@/app/url";
import { AuthActions } from "@/lib/auth";
import _ from "lodash";
import type React from "react";
import { useState } from "react";
import { useLocalStorage } from "usehooks-ts";
import ChatControls from "./chat-controls";
import ChatHeader from "./chat-header";
import ErrorDisplay from "./error-display";
import type { MessageHistory } from "./types";

const baseUrl = getUrl();
const base = new URL(baseUrl).host;
const protocol = process.env.NODE_ENV === "development" ? "ws" : "wss";

export default function AiSidebarChat() {
  const { activeFile, lineageData, branchId } = useFiles();

  const [isLoading, setIsLoading] = useState(false);
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [contextFiles, setContextFiles] = useState<FileNode[]>([]);
  const [messageHistory, setMessageHistory] = useLocalStorage<MessageHistory>(
    LocalStorageKeys.aiMessageHistory(branchId),
    [],
  );

  const visibleLineage = lineageData[activeFile?.node.path || ""] || null;
  const { getToken } = AuthActions();
  const accessToken = getToken("access");

  const resetState = () => {
    setIsLoading(false);
    setInput("");
    setError(null);
    setContextFiles([]);
    setMessageHistory([]);
  };

  const { startWebSocket, sendMessage, stopWebSocket } = useWebSocket(
    `${protocol}://${base}/ws/infer/?token=${accessToken}`,
    {
      onOpen: () => {
        sendMessage(
          JSON.stringify({
            current_file: activeFile?.content || "",
            asset_id: visibleLineage?.data?.asset_id,
            related_assets: visibleLineage?.data?.assets,
            asset_links: visibleLineage?.data?.asset_links,
            column_links: visibleLineage?.data?.column_links,
            instructions: input,
          }),
        );
      },
      onClose: () => {
        console.log("WebSocket disconnected");
        setIsLoading(false);
      },
      onMessage: ({ event }) => {
        const data = JSON.parse(event.data);
        if (data.type === "message_chunk") {
          setMessageHistory((prev) => {
            const lastMessage = prev[prev.length - 1];
            const updatedLastMessage = {
              ...lastMessage,
              content: lastMessage.content + data.content,
            };
            return [...prev.slice(0, -1), updatedLastMessage];
          });
        } else if (data.type === "message_end") {
          setIsLoading(false);
          stopWebSocket();
        } else if (data.type === "error") {
          setError(data.message);
          stopWebSocket();
          setIsLoading(false);
        }
      },
      onError: ({ event }) => {
        console.error("WebSocket error:", event);
        setIsLoading(false);
        stopWebSocket();
      },
    },
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessageHistory((prev) => [
      ...prev,
      { id: _.uniqueId(), role: "user" as const, content: input },
      { id: _.uniqueId(), role: "assistant" as const, content: "" },
    ]);
    setInput("");
    setError(null);
    setIsLoading(true);
    startWebSocket();
  };

  return (
    <div className="flex flex-col w-full h-full">
      <ChatHeader resetState={resetState} />
      {messageHistory.length === 0 ? (
        <ChatControls
          input={input}
          setInput={setInput}
          isLoading={isLoading}
          handleSubmit={handleSubmit}
          activeFile={activeFile}
          lineageData={visibleLineage}
          contextFiles={contextFiles}
          setContextFiles={setContextFiles}
        />
      ) : (
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex flex-col flex-1 overflow-y-auto hide-scrollbar text-sm gap-4">
            {messageHistory.map((message) => (
              <div
                key={message.id}
                className={`${
                  message.role === "user"
                    ? " bg-background p-2 rounded-md"
                    : "p-1 mb-8"
                }`}
              >
                {message.content}
              </div>
            ))}
          </div>
          <ChatControls
            input={input}
            setInput={setInput}
            isLoading={isLoading}
            handleSubmit={handleSubmit}
            activeFile={activeFile}
            lineageData={visibleLineage}
            contextFiles={contextFiles}
            setContextFiles={setContextFiles}
          />
        </div>
      )}
      <ErrorDisplay error={error} />
    </div>
  );
}
