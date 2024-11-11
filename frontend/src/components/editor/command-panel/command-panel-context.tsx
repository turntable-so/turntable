import {LocalStorageKeys} from "@/app/constants/local-storage-keys";
import {useWebSocket} from "@/app/hooks/use-websocket";
import getUrl from "@/app/url";
import {addRecentCommand, getCommandOptions,} from "@/components/editor/command-panel/command-panel-options";
import {useBottomPanelTabs} from "@/components/editor/use-bottom-panel-tabs";
import {AuthActions} from "@/lib/auth";
import {
  createContext,
  type Dispatch,
  type FC,
  type ReactNode,
  type SetStateAction,
  useContext,
  useRef,
  useState,
} from "react";
import {useLocalStorage} from "usehooks-ts";
import type {Command, CommandPanelState, CommandStatus,} from "./command-panel-types";
import {useFiles} from "@/app/contexts/FilesContext";

interface CommandPanelContextType {
  commandPanelState: CommandPanelState;
  selectedCommandIndex: number;
  setSelectedCommandIndex: Dispatch<SetStateAction<number>>;
  commandHistory: Command[];
  updateCommandLogById: (id: string, newLog: string) => void;
  updateCommandById: (
    id: string,
    {
      status,
      duration,
    }: {
      status?: CommandStatus;
      duration?: string;
    },
  ) => void;
  runCommand: () => void;
  runCommandFromSearchBar: (command: string) => void;
  inputValue: string;
  setInputValue: Dispatch<SetStateAction<string>>;
  commandOptions: string[];
  setCommandOptions: Dispatch<SetStateAction<string[]>>;
}

const defaultContextValue: CommandPanelContextType = {
  commandPanelState: "idling",
  selectedCommandIndex: 0,
  setSelectedCommandIndex: () => {},
  commandHistory: [],
  updateCommandLogById: () => {},
  updateCommandById: () => {},
  runCommand: () => {},
  runCommandFromSearchBar: () => {},
  inputValue: "",
  setInputValue: () => {},
  commandOptions: [],
  setCommandOptions: () => {},
};

const CommandPanelContext =
  createContext<CommandPanelContextType>(defaultContextValue);

export const useCommandPanelContext = (): CommandPanelContextType => {
  const context = useContext(CommandPanelContext);
  if (!context) {
    throw new Error("useCommandPanelContext must be used within a MyProvider");
  }
  return context;
};

interface CommandPanelProviderProps {
  children: ReactNode;
}

export const CommandPanelProvider: FC<CommandPanelProviderProps> = ({
  children,
}) => {
  const { branchId, fetchFiles } = useFiles();

  const [inputValue, setInputValue] = useState<string>("");
  const [commandOptions, setCommandOptions] = useState<string[]>([]);
  const [commandPanelState, setCommandPanelState] =
    useState<CommandPanelState>("idling");
  const [selectedCommandIndex, setSelectedCommandIndex] = useState<number>(0);
  const [commandHistory, setCommandHistory] = useLocalStorage<Command[]>(
    LocalStorageKeys.commandHistory(branchId || ""),
    [],
  );
  const [_, setActiveTab] = useBottomPanelTabs({ branchId: branchId || "" });
  const MAX_COMMAND_HISTORY_SIZE = 20;

  const addCommandToHistory = (newCommand: Command) => {
    setCommandHistory((prevHistory) => {
      const updatedHistory = [newCommand, ...prevHistory];
      if (updatedHistory.length > MAX_COMMAND_HISTORY_SIZE) {
        updatedHistory.pop();
      }
      return updatedHistory;
    });
  };

  const updateCommandLogById = (id: string, newLog: string) => {
    setCommandHistory((prevHistory) => {
      const index = prevHistory.findIndex((command) => command.id === id);
      if (index === -1) return prevHistory;
      const newHistory = [...prevHistory];
      newHistory[index] = {
        ...newHistory[index],
        logs: [...(newHistory[index].logs || []), newLog],
      };
      return newHistory;
    });
  };

  const updateCommandById = (
    id: string,
    {
      status,
      duration,
    }: {
      status?: CommandStatus;
      duration?: string;
    },
  ) => {
    setCommandHistory((prevHistory) => {
      const index = prevHistory.findIndex((command) => command.id === id);
      if (index === -1) return prevHistory;
      const newHistory = [...prevHistory];
      newHistory[index] = {
        ...newHistory[index],
        status: status || newHistory[index].status,
        duration: duration || newHistory[index].duration,
      };
      return newHistory;
    });
  };

  /*********************************************************
   * WEBSOCKETS *
   *********************************************************/
  const newCommandIdRef = useRef<string>("");
  const { getToken } = AuthActions();
  const accessToken = getToken("access");

  const baseUrl = getUrl();
  const base = new URL(baseUrl).host;
  const protocol = process.env.NODE_ENV === "development" ? "ws" : "wss";

  const { startWebSocket, sendMessage, stopWebSocket } = useWebSocket<{
    command: string;
  }>(`${protocol}://${base}/ws/dbt_command/?token=${accessToken}`, {
    onOpen: ({ payload }) => {
      sendMessage(
        JSON.stringify({ action: "start", command: payload.command, branch_id: branchId }),
      );
      setInputValue("");
    },
    onMessage: ({ event }) => {
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
      } else if (event.data === "WORKFLOW_STARTED") {
        return;
      } else if (event.data === "WORKFLOW_CANCELLED") {
        setCommandPanelState("idling");
        updateCommandById(newCommandIdRef.current, { status: "cancelled" });
        stopWebSocket();
      } else {
        updateCommandLogById(newCommandIdRef.current, event.data);
      }
    },
    onError: ({ event }) => {
      updateCommandLogById(
        newCommandIdRef.current,
        `WebSocket error: ${event}`,
      );
      setCommandPanelState("idling");
      updateCommandById(newCommandIdRef.current, { status: "failed" });
    },
    onClose: () => {
      setCommandPanelState("idling");
      fetchFiles();
    },
  });

  const _runCommandCore = (command?: string) => {
    const payloadCommand = command ?? inputValue;
    startWebSocket({ command: payloadCommand });
    setCommandPanelState("running");

    const commandId = Date.now().toString();
    newCommandIdRef.current = commandId;
    addCommandToHistory({
      id: commandId,
      command: payloadCommand,
      status: "running",
      time: new Date().toLocaleTimeString(),
    });

    setSelectedCommandIndex(0);
    const trimmedInputValue = inputValue.trim();
    if (trimmedInputValue) {
      addRecentCommand(trimmedInputValue);
      setCommandOptions(getCommandOptions());
    }
  };

  const runCommand = () => {
    if (commandPanelState === "running") {
      sendMessage(JSON.stringify({ action: "cancel" }));
      setCommandPanelState("cancelling");
      return;
    }

    if (!inputValue || commandPanelState === "cancelling") {
      return;
    }

    _runCommandCore();
  };

  const runCommandFromSearchBar = (command: string) => {
    setActiveTab("command");
    _runCommandCore(command);
  };

  return (
    <CommandPanelContext.Provider
      value={{
        commandPanelState,
        selectedCommandIndex,
        setSelectedCommandIndex,
        commandHistory,
        updateCommandLogById,
        updateCommandById,
        runCommand,
        runCommandFromSearchBar,
        inputValue,
        setInputValue,
        commandOptions,
        setCommandOptions,
      }}
    >
      {children}
    </CommandPanelContext.Provider>
  );
};
