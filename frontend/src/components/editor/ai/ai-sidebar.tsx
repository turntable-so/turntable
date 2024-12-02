import { LocalStorageKeys } from "@/app/constants/local-storage-keys";
import {
  type FileNode,
  type OpenedFile,
  useFiles,
} from "@/app/contexts/FilesContext";
import type { Asset, Lineage } from "@/app/contexts/LineageView";
import { useWebSocket } from "@/app/hooks/use-websocket";
import getUrl from "@/app/url";
import { AuthActions } from "@/lib/auth";
import _ from "lodash";
import { Loader2 } from "lucide-react";
import type React from "react";
import { useEffect, useRef, useState } from "react";
import { useLocalStorage } from "usehooks-ts";
import ChatControls from "./chat-controls";
import ChatHeader from "./chat-header";
import { SUPPORTED_AI_MODELS } from "./constants";
import ErrorDisplay from "./error-display";
import ResponseDisplay from "./response-display";
import type { Message } from "./types";

const baseUrl = getUrl();
const base = new URL(baseUrl).host;
const protocol = process.env.NODE_ENV === "development" ? "ws" : "wss";

type MessageHistoryPayload = {
  model: string;
  current_file: string;
  asset_id: string | undefined;
  related_assets: Asset[] | undefined;
  asset_links: any | undefined;
  column_links: any | undefined;
  message_history: Omit<Message, "id">[];
};

export default function AiSidebarChat() {
  const { activeFile, lineageData, branchId } = useFiles();
  const visibleLineage = lineageData[activeFile?.node.path || ""] || null;

  const [isLoading, setIsLoading] = useState(false);
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [contextFiles, setContextFiles] = useState<FileNode[]>([]);
  const [messageHistory, setMessageHistory] = useLocalStorage<Array<Message>>(
    LocalStorageKeys.aiMessageHistory(branchId),
    [],
  );
  const [selectedModel, setSelectedModel] = useLocalStorage<string>(
    LocalStorageKeys.aiSelectedModel(branchId),
    SUPPORTED_AI_MODELS[0],
  );
  const [aiActiveFile, setAiActiveFile] = useState<OpenedFile | null>(null);
  const [aiLineageContext, setAiLineageContext] = useState<Lineage | null>(
    null,
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { getToken } = AuthActions();
  const accessToken = getToken("access");

  const resetState = () => {
    setIsLoading(false);
    setInput("");
    setError(null);
    setContextFiles([]);
    setMessageHistory([]);
  };

  const { startWebSocket, sendMessage, stopWebSocket } =
    useWebSocket<MessageHistoryPayload>(
      `${protocol}://${base}/ws/infer/?token=${accessToken}`,
      {
        onOpen: ({ payload }) => {
          sendMessage(JSON.stringify(payload));
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
            setIsLoading(false);
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

    const newMessageHistory = [
      ...messageHistory,
      { id: _.uniqueId(), role: "user" as const, content: input },
    ];

    setMessageHistory(newMessageHistory);
    setInput("");
    setError(null);
    setIsLoading(true);

    const currentFileContent =
      typeof aiActiveFile?.content === "string" ? aiActiveFile?.content : "";

    const payload: MessageHistoryPayload = {
      model: selectedModel,
      current_file: currentFileContent,
      asset_id: aiLineageContext?.asset_id,
      related_assets: aiLineageContext?.assets,
      asset_links: aiLineageContext?.asset_links,
      column_links: aiLineageContext?.column_links,
      message_history: newMessageHistory.map(({ id, ...rest }) => ({
        ...rest,
      })),
    };
    startWebSocket(payload);

    // append a new assistant message to the end of the history (optimistic update)
    setMessageHistory((prev) => [
      ...prev,
      { id: _.uniqueId(), role: "assistant" as const, content: "" },
    ]);

    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    setAiActiveFile(activeFile);
  }, [activeFile]);

  useEffect(() => {
    setAiLineageContext(visibleLineage?.data);
  }, [visibleLineage]);

  return (
    <div className="flex flex-col w-full h-full">
      <ChatHeader resetState={resetState} />
      {messageHistory.length === 0 ? (
        <ChatControls
          input={input}
          setInput={setInput}
          isLoading={isLoading}
          handleSubmit={handleSubmit}
          aiActiveFile={aiActiveFile}
          setAiActiveFile={setAiActiveFile}
          aiLineageContext={aiLineageContext}
          setAiLineageContext={setAiLineageContext}
          contextFiles={contextFiles}
          setContextFiles={setContextFiles}
          selectedModel={selectedModel}
          setSelectedModel={setSelectedModel}
        />
      ) : (
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex flex-col flex-1 overflow-y-auto hide-scrollbar text-sm gap-4">
            {messageHistory.map((message, index) => (
              <div
                key={message.id}
                className={`${
                  message.role === "user"
                    ? " bg-background p-2 rounded-md"
                    : index === messageHistory.length - 1
                      ? "p-1 mb-96"
                      : "p-1 mb-8"
                }`}
              >
                {message.role === "user" ? (
                  message.content
                ) : (
                  <ResponseDisplay content={message.content} />
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex items-center justify-center">
                <Loader2 className="w-4 h-4 animate-spin" />
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <ChatControls
            input={input}
            setInput={setInput}
            isLoading={isLoading}
            handleSubmit={handleSubmit}
            aiActiveFile={aiActiveFile}
            setAiActiveFile={setAiActiveFile}
            aiLineageContext={aiLineageContext}
            setAiLineageContext={setAiLineageContext}
            contextFiles={contextFiles}
            setContextFiles={setContextFiles}
            selectedModel={selectedModel}
            setSelectedModel={setSelectedModel}
          />
        </div>
      )}
      <ErrorDisplay error={error} />
    </div>
  );
}
