import { type FileNode, useFiles } from "@/app/contexts/FilesContext";
import { useWebSocket } from "@/app/hooks/use-websocket";
import getUrl from "@/app/url";
import { AuthActions } from "@/lib/auth";
import type React from "react";
import { useState } from "react";
import History from "./ai-history";
import ChatControls from "./chat-controls";
import ChatHeader from "./chat-header";
import ErrorDisplay from "./error-display";
import ResponseDisplay from "./response-display";

const baseUrl = getUrl();
const base = new URL(baseUrl).host;
const protocol = process.env.NODE_ENV === "development" ? "ws" : "wss";

export default function AiSidebarChat() {
  const [isLoading, setIsLoading] = useState(false);
  const [input, setInput] = useState("");
  const [currentResponse, setCurrentResponse] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<"chat" | "history">("chat");
  const [contextFiles, setContextFiles] = useState<FileNode[]>([]);

  const { activeFile, lineageData } = useFiles();
  const visibleLineage = lineageData[activeFile?.node.path || ""] || null;
  const { getToken } = AuthActions();
  const accessToken = getToken("access");

  const resetState = () => {
    setInput("");
    setCurrentResponse("");
    setError(null);
    setContextFiles([]);
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
          setCurrentResponse((prev) => prev + data.content);
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
    setIsLoading(true);
    startWebSocket();
    resetState();
  };

  return (
    <div className="flex flex-col w-full h-full overflow-y-scroll hide-scrollbar">
      <ChatHeader setView={setView} resetState={resetState} />
      {view === "chat" ? (
        <div>
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
          <ResponseDisplay response={currentResponse} />
          <ErrorDisplay error={error} />
        </div>
      ) : (
        <History />
      )}
    </div>
  );
}
