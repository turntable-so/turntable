import { useFiles } from "@/app/contexts/FilesContext";
import { useWebSocket } from "@/app/hooks/use-websocket";
import getUrl from "@/app/url";
import { AuthActions } from "@/lib/auth";
import _ from "lodash";
import type React from "react";
import { useRef } from "react";
import AiMessageBox from "./ai-message-box";
import { useAISidebar } from "./ai-sidebar-context";
import ChatControls from "./chat-controls";
import ChatHeader from "./chat-header";
import ErrorDisplay from "./error-display";
import type { AIMessage, MessageHistoryPayload } from "./types";

const baseUrl = getUrl();
const base = new URL(baseUrl).host;
const protocol = process.env.NODE_ENV === "development" ? "ws" : "wss";

export default function AiSidebarChat() {
  const { branchId } = useFiles();
  const {
    setIsLoading,
    input,
    setInput,
    error,
    setError,
    messageHistory,
    setMessageHistory,
    aiActiveFile,
    aiLineageContext,
    contextFiles,
    setContextFiles,
    selectedModel,
    aiContextPreview,
    aiCompiledSql,
  } = useAISidebar();

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

  const { startWebSocket, sendMessage, stopWebSocket, isConnected } =
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

  const handleSubmit = async (
    e: React.FormEvent | null,
    messageHistoryOverride?: AIMessage[],
  ) => {
    if (e) e.preventDefault();

    const newMessageHistory = messageHistoryOverride || [
      ...messageHistory,
      { id: _.uniqueId(), role: "user" as const, content: input },
    ];

    if (!messageHistoryOverride) {
      setMessageHistory(newMessageHistory);
      setInput("");
    }

    setError(null);
    setIsLoading(true);

    const payload: MessageHistoryPayload = {
      project_id: branchId,
      model: selectedModel,
      context_files: [
        ...(aiActiveFile?.node.path ? [aiActiveFile.node.path] : []),
        ...contextFiles.map((file) => file.path),
      ],
      context_preview: aiContextPreview?.table ?? null,
      asset_id: aiLineageContext?.asset_id,
      related_assets: aiLineageContext?.assets,
      asset_links: aiLineageContext?.asset_links,
      column_links: aiLineageContext?.column_links,
      message_history: newMessageHistory.map(({ id, ...rest }) => rest),
      compiled_query: aiCompiledSql?.compiled_query ?? null,
    };
    startWebSocket(payload);

    // Append assistant's placeholder message after we send the message
    setMessageHistory((prev) => [
      ...prev,
      { id: _.uniqueId(), role: "assistant" as const, content: "" },
    ]);

    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleEditMessage = (index: number, newContent: string) => {
    const newMessageHistory = messageHistory.slice(0, index + 1);
    newMessageHistory[index] = {
      ...newMessageHistory[index],
      content: newContent,
    };
    setMessageHistory(newMessageHistory);
    setMessageHistory((prev) => prev.slice(0, index + 1));
    stopWebSocket();
    handleSubmit(null, newMessageHistory);
  };

  return (
    <div className="flex flex-col w-full h-full">
      <ChatHeader resetState={resetState} />
      {messageHistory.length === 0 ? (
        <ChatControls
          isConnected={isConnected}
          handleSubmit={handleSubmit}
          stopWebSocket={stopWebSocket}
        />
      ) : (
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex flex-col flex-1 overflow-y-auto hide-scrollbar text-sm gap-4">
            {messageHistory.map((message, index) => (
              <AiMessageBox
                key={message.id}
                isConnected={isConnected}
                stopWebSocket={stopWebSocket}
                message={message}
                isLastMessage={index === messageHistory.length - 1}
                index={index}
                onEditMessage={handleEditMessage}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>
          <ChatControls
            isConnected={isConnected}
            handleSubmit={handleSubmit}
            stopWebSocket={stopWebSocket}
          />
        </div>
      )}
      <ErrorDisplay error={error} />
    </div>
  );
}
