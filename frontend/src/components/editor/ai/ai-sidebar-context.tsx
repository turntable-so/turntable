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
import type {
  AICompiledSql,
  AICustomSelections,
  AIFileProblems,
  AIMessage,
  AIQueryPreview,
} from "./types";
import { generatePreviewForAI } from "./utils";

interface AISidebarContextType {
  isLoading: boolean;
  setIsLoading: Dispatch<SetStateAction<boolean>>;
  input: string;
  setInput: Dispatch<SetStateAction<string>>;
  error: string | null;
  setError: Dispatch<SetStateAction<string | null>>;
  contextFiles: FileNode[];
  setContextFiles: Dispatch<SetStateAction<FileNode[]>>;
  aiContextPreview: AIQueryPreview | null;
  setAiContextPreview: Dispatch<SetStateAction<AIQueryPreview | null>>;
  messageHistory: AIMessage[];
  setMessageHistory: Dispatch<SetStateAction<AIMessage[]>>;
  selectedModel: string;
  setSelectedModel: Dispatch<SetStateAction<string>>;
  aiActiveFile: OpenedFile | null;
  setAiActiveFile: Dispatch<SetStateAction<OpenedFile | null>>;
  aiLineageContext: Lineage | null;
  setAiLineageContext: Dispatch<SetStateAction<Lineage | null>>;
  aiCompiledSql: AICompiledSql | null;
  setAiCompiledSql: Dispatch<SetStateAction<AICompiledSql | null>>;
  aiFileProblems: AIFileProblems | null;
  setAiFileProblems: Dispatch<SetStateAction<AIFileProblems | null>>;
  aiCustomSelections: AICustomSelections[] | null;
  setAiCustomSelections: Dispatch<SetStateAction<AICustomSelections[] | null>>;
}

const AISidebarContext = createContext<AISidebarContextType | undefined>(
  undefined,
);

interface AISidebarProviderProps {
  children: ReactNode;
}

export function AISidebarProvider({ children }: AISidebarProviderProps) {
  const { branchId, activeFile, lineageData, queryPreviewData, compiledSql } =
    useFiles();

  const [isLoading, setIsLoading] = useState(false);
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [contextFiles, setContextFiles] = useState<FileNode[]>([]);
  const [aiContextPreview, setAiContextPreview] =
    useState<AIQueryPreview | null>(null);
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
  const [aiCompiledSql, setAiCompiledSql] = useState<AICompiledSql | null>(
    null,
  );
  const [aiFileProblems, setAiFileProblems] = useState<AIFileProblems | null>(
    null,
  );
  const [aiCustomSelections, setAiCustomSelections] = useState<AICustomSelections[] | null>(
    null,
  );

  const visibleLineage = lineageData[activeFile?.node.path || ""] || null;

  useEffect(() => {
    setAiActiveFile(activeFile);
    setAiFileProblems(null);
  }, [activeFile]);

  useEffect(() => {
    setAiLineageContext(visibleLineage?.data);
  }, [visibleLineage]);

  useEffect(() => {
    if (queryPreviewData?.rows && queryPreviewData?.cols && activeFile) {
      const table = generatePreviewForAI(
        queryPreviewData.rows,
        queryPreviewData.cols,
      );
      setAiContextPreview({
        table,
        file_name: queryPreviewData.file_name,
      });
    }
  }, [queryPreviewData]);

  useEffect(() => {
    if (activeFile && compiledSql) {
      setAiCompiledSql({
        compiled_query: compiledSql.sql,
        file_name: compiledSql.file_name,
      });
      return;
    }

    setAiCompiledSql(null);
  }, [compiledSql]);

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
        aiContextPreview,
        setAiContextPreview,
        messageHistory,
        setMessageHistory,
        selectedModel,
        setSelectedModel,
        aiActiveFile,
        setAiActiveFile,
        aiLineageContext,
        setAiLineageContext,
        aiCompiledSql,
        setAiCompiledSql,
        aiFileProblems,
        setAiFileProblems,
        aiCustomSelections,
        setAiCustomSelections,
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
