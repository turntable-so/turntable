import { LocalStorageKeys } from "@/app/constants/local-storage-keys";
import {
  type FileNode,
  type OpenedFile,
  useFiles,
} from "@/app/contexts/FilesContext";
import type { Lineage } from "@/app/contexts/LineageView";
import {
  type Dispatch,
  type ReactNode,
  type SetStateAction,
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";
import { useLocalStorage } from "usehooks-ts";
import { SUPPORTED_AI_MODELS } from "./constants";
import type { AIMessage } from "./types";

interface AISidebarContextType {
  isLoading: boolean;
  setIsLoading: Dispatch<SetStateAction<boolean>>;
  input: string;
  setInput: Dispatch<SetStateAction<string>>;
  error: string | null;
  setError: Dispatch<SetStateAction<string | null>>;
  contextFiles: FileNode[];
  setContextFiles: Dispatch<SetStateAction<FileNode[]>>;
  contextPreview: string | null;
  setContextPreview: Dispatch<SetStateAction<string | null>>;
  messageHistory: AIMessage[];
  setMessageHistory: Dispatch<SetStateAction<AIMessage[]>>;
  selectedModel: string;
  setSelectedModel: Dispatch<SetStateAction<string>>;
  aiActiveFile: OpenedFile | null;
  setAiActiveFile: Dispatch<SetStateAction<OpenedFile | null>>;
  aiLineageContext: Lineage | null;
  setAiLineageContext: Dispatch<SetStateAction<Lineage | null>>;
}

const AISidebarContext = createContext<AISidebarContextType | undefined>(
  undefined,
);

interface AISidebarProviderProps {
  children: ReactNode;
}

export function AISidebarProvider({ children }: AISidebarProviderProps) {
  const { branchId, activeFile, lineageData, rowData, colDefs } = useFiles();

  const [isLoading, setIsLoading] = useState(false);
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [contextFiles, setContextFiles] = useState<FileNode[]>([]);
  const [contextPreview, setContextPreview] = useState<string | null>(null);
  const [messageHistory, setMessageHistory] = useLocalStorage<Array<AIMessage>>(
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

  const visibleLineage = lineageData[activeFile?.node.path || ""] || null;

  useEffect(() => {
    setAiActiveFile(activeFile);
  }, [activeFile]);

  useEffect(() => {
    setAiLineageContext(visibleLineage?.data);
  }, [visibleLineage]);

  useEffect(() => {
    if (rowData && colDefs) {
      const columns = colDefs.map((col) => col.field);
      const headers = colDefs.map((col) => col.headerName);
      const topRows = rowData.slice(0, 5);

      let table = `| ${headers.join(" | ")} |\n`;
      table += `| ${headers.map(() => "---").join(" | ")} |\n`;
      topRows.forEach((row) => {
        table += `| ${columns.map((field) => String(row[field])).join(" | ")} |\n`;
      });

      setContextPreview(table);
    }
  }, [rowData, colDefs]);

  return (
    <AISidebarContext.Provider
      value={{
        isLoading,
        setIsLoading,
        input,
        setInput,
        error,
        setError,
        contextFiles,
        setContextFiles,
        contextPreview,
        setContextPreview,
        messageHistory,
        setMessageHistory,
        selectedModel,
        setSelectedModel,
        aiActiveFile,
        setAiActiveFile,
        aiLineageContext,
        setAiLineageContext,
      }}
    >
      {children}
    </AISidebarContext.Provider>
  );
}

export function useAISidebar() {
  const context = useContext(AISidebarContext);
  if (context === undefined) {
    throw new Error("useAISidebar must be used within an AISidebarProvider");
  }
  return context;
}
