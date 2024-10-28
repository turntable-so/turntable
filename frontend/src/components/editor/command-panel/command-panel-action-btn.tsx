import { useWebSocket } from "@/app/hooks/use-websocket";
import getUrl from "@/app/url";
import { AuthActions } from "@/lib/auth";
import { CircleSlash, CornerDownLeft, Command as PlayIcon } from "lucide-react";
import { Loader2 } from "lucide-react";
import { useEffect, useRef } from "react";
import { Button } from "../../ui/button";
import { useCommandPanelContext } from "./command-panel-context";

const baseUrl = getUrl();
const base = new URL(baseUrl).host;
const protocol = process.env.NODE_ENV === "development" ? "ws" : "wss";

type CommandPanelActionBtnProps = {
  inputValue: string;
  setInputValue: (value: string) => void;
  onRunCommand: () => void;
};

export default function CommandPanelActionBtn({
  inputValue,
  setInputValue,
  onRunCommand,
}: CommandPanelActionBtnProps) {
  const { getToken } = AuthActions();
  const accessToken = getToken("access");

  const {
    commandPanelState,
    setCommandPanelState,
    addCommandToHistory,
    updateCommandLogById,
    setSelectedCommandIndex,
    updateCommandById,
  } = useCommandPanelContext();
  const newCommandIdRef = useRef<string>("");

  const componentMap = {
    idling: (
      <div className="flex flex-row gap-0.5 items-center mr-2 text-base">
        <PlayIcon className="h-4 w-4 mr-0.5" />
        <CornerDownLeft className="h-4 w-4 mr-2" /> Run
      </div>
    ),
    running: (
      <div className="flex flex-row gap-2 items-center">
        <CircleSlash className="h-4 w-4 mr-2" />
        Cancel
      </div>
    ),
    cancelling: (
      <div className="flex flex-row gap-2 items-center">
        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
        Cancelling
      </div>
    ),
  };

  const isDisabled = commandPanelState === "cancelling";

  // TODO: pass in branch id when we support branches
  const { startWebSocket, sendMessage, stopWebSocket } = useWebSocket(
    `${protocol}://${base}/ws/dbt_command/?token=${accessToken}`,
    {
      onOpen: () => {
        sendMessage(JSON.stringify({ action: "start", command: inputValue }));
        setInputValue("");
      },
      onMessage: (event) => {
        if (event.data.error) {
          setCommandPanelState("idling");
          updateCommandById(newCommandIdRef.current, { status: "failed" });
        } else if (event.data === "PROCESS_STREAM_SUCCESS") {
          setCommandPanelState("idling");
          updateCommandById(newCommandIdRef.current, {
            status: "success",
            duration: `${Math.round((Date.now() - Number.parseInt(newCommandIdRef.current)) / 1000)}s`,
          });
        } else if (event.data === "PROCESS_STREAM_ERROR") {
          setCommandPanelState("idling");
          updateCommandById(newCommandIdRef.current, { status: "failed" });
        } else if (event.data === "WORKFLOW_CANCELLED") {
          setCommandPanelState("idling");
          updateCommandById(newCommandIdRef.current, { status: "cancelled" });
          stopWebSocket();
        } else {
          updateCommandLogById(newCommandIdRef.current, event.data);
        }
      },
      onError: (event) => {
        console.error("WebSocket error:", event);
        updateCommandLogById(
          newCommandIdRef.current,
          `WebSocket error: ${event}`,
        );
        setCommandPanelState("idling");
        updateCommandById(newCommandIdRef.current, { status: "failed" });
      },
      onClose: () => {
        setCommandPanelState("idling");
      },
    },
  );

  const handleRunCommand = () => {
    if (commandPanelState === "running") {
      sendMessage(JSON.stringify({ action: "cancel" }));
      setCommandPanelState("cancelling");
      return;
    }

    if (!inputValue || commandPanelState === "cancelling") {
      return;
    }

    startWebSocket();
    setCommandPanelState("running");

    const commandId = Date.now().toString();
    newCommandIdRef.current = commandId;
    addCommandToHistory({
      id: commandId,
      command: inputValue,
      status: "running",
      time: new Date().toLocaleTimeString(),
    });
    setSelectedCommandIndex(0);
    onRunCommand();
  };

  const handleCommandEnterShortcut = () => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
        event.preventDefault();
        handleRunCommand();
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  };
  useEffect(handleCommandEnterShortcut, [inputValue]);

  return (
    <Button
      size="sm"
      variant="outline"
      onClick={handleRunCommand}
      disabled={isDisabled}
    >
      {componentMap[commandPanelState]}
    </Button>
  );
}
