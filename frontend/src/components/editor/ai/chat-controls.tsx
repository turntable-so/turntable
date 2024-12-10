import type { FileNode } from "@/app/contexts/FilesContext";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { CircleAlert, CornerDownLeft, DatabaseZap, Loader2, Network, Plus, Table, X, XCircle } from "lucide-react";
import type React from "react";
import { useEffect, useRef, useState } from "react";
import { Button } from "../../ui/button";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../../ui/select";
import { Textarea } from "../../ui/textarea";
import { useAISidebar } from "./ai-sidebar-context";
import { SUPPORTED_AI_MODELS } from "./constants";
import FileExplorer from "./file-explorer";

interface ChatControlsProps {
  isConnected: boolean;
  handleSubmit: (e: React.FormEvent) => void;
  stopWebSocket: () => void;
  autoFocus?: boolean;
}

export default function ChatControls({
  isConnected,
  handleSubmit,
  stopWebSocket,
  autoFocus = false,
}: ChatControlsProps) {
  const {
    input,
    setInput,
    isLoading,
    aiActiveFile,
    setAiActiveFile,
    aiLineageContext,
    setAiLineageContext,
    contextFiles,
    setContextFiles,
    selectedModel,
    setSelectedModel,
    aiContextPreview,
    setAiContextPreview,
    aiCompiledSql,
    setAiCompiledSql,
    aiFileProblems,
    setAiFileProblems,
  } = useAISidebar();

  const [isFileExplorerOpen, setIsFileExplorerOpen] = useState(false);
  const numberOfLineageFiles = aiLineageContext?.assets?.length || 0;
  const lineageContextString =
    aiLineageContext?.assets?.map((asset) => asset.name).join(", ") || "";
  const displayLineageContextString =
    lineageContextString.length > 50
      ? `${lineageContextString.slice(0, 50)}...`
      : lineageContextString;
  const handleRemoveAiActiveFile = () => {
    setAiActiveFile(null);
  };

  const handleRemoveLineageContext = () => {
    setAiLineageContext(null);
  };

  const handleRemoveContextFile = (file: FileNode) => {
    setContextFiles((prev) => prev.filter((f) => f.path !== file.path));
  };

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  useEffect(() => {
    if (autoFocus && textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.setSelectionRange(input.length, input.length);
    }
  }, [autoFocus, input]);

  return (
    <div className="relative">
      {isConnected && (
        <div className="absolute inset-x-0 -top-12 flex justify-center z-50">
          <Button
            size="sm"
            variant="outline"
            className="px-4 py-2 flex items-center gap-2"
            onClick={stopWebSocket}
          >
            Cancel <XCircle className="h-4 w-4" />
          </Button>
        </div>
      )}
      <div className="flex flex-col bg-background rounded-md p-2 gap-2">
        <div className="flex gap-1 flex-wrap min-h-6">
          <div
            className="hover:bg-muted rounded-md px-0.5 cursor-pointer border flex items-center justify-center relative"
            onClick={() => setIsFileExplorerOpen((prev) => !prev)}
          >
            <Plus className="w-4 h-4" />

            {isFileExplorerOpen && (
              <div className="absolute left-0 top-full mt-1 z-10">
                <FileExplorer
                  onClose={() => setIsFileExplorerOpen(false)}
                  setContextFiles={setContextFiles}
                />
              </div>
            )}
          </div>

          {aiActiveFile ? (
            <div className="bg-muted/50 rounded-md p-1 text-xs flex items-center justify-between gap-1">
              {aiActiveFile.node.name}{" "}
              <span
                className="text-[10px] text-muted-foreground cursor-pointer"
                onClick={handleRemoveAiActiveFile}
              >
                <X className="w-[0.6rem] h-[0.6rem]" />
              </span>
            </div>
          ) : null}

          {numberOfLineageFiles > 0 ? (
            <Tooltip delayDuration={100}>
              <TooltipTrigger asChild>
                <div className="bg-muted/50 rounded-md p-1 text-xs flex items-center justify-between gap-1">
                  <Network className="w-3 h-3" />
                  {numberOfLineageFiles}{" "}
                  <span className="text-[10px] text-muted-foreground">
                    models from lineage
                  </span>
                  <span
                    className="text-[10px] text-muted-foreground cursor-pointer"
                    onClick={handleRemoveLineageContext}
                  >
                    <X className="w-[0.6rem] h-[0.6rem]" />
                  </span>
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p>{displayLineageContextString}</p>
              </TooltipContent>
            </Tooltip>
          ) : null}

          {contextFiles.map((file) => (
            <div
              key={file.path}
              className="bg-muted/50 rounded-md p-1 text-xs flex items-center justify-between gap-1"
            >
              {file.name}{" "}
              <span className="text-[10px] text-muted-foreground">File</span>
              <span
                className="text-[10px] text-muted-foreground cursor-pointer"
                onClick={() => handleRemoveContextFile(file)}
              >
                <X className="w-[0.6rem] h-[0.6rem]" />
              </span>
            </div>
          ))}

          {aiContextPreview && (
            <div className="bg-muted/50 rounded-md p-1 text-xs flex items-center justify-between gap-1">
              <Table className="w-3 h-3" />
              Preview
              <span className="text-[10px] text-muted-foreground">
                {aiContextPreview.file_name}
              </span>
              <span
                className="text-[10px] text-muted-foreground cursor-pointer"
                onClick={() => setAiContextPreview(null)}
              >
                <X className="w-[0.6rem] h-[0.6rem]" />
              </span>
            </div>
          )}

          {aiCompiledSql && (
            <div className="bg-muted/50 rounded-md p-1 text-xs flex items-center justify-between gap-1">
              <DatabaseZap className="w-3 h-3" />
              Compiled SQL
              <span className="text-[10px] text-muted-foreground">
                {aiCompiledSql.file_name}
              </span>
              <span
                className="text-[10px] text-muted-foreground cursor-pointer"
                onClick={() => setAiCompiledSql(null)}
              >
                <X className="w-[0.6rem] h-[0.6rem]" />
              </span>
            </div>
          )}

          {aiFileProblems && (
            <div className="bg-muted/50 rounded-md p-1 text-xs flex items-center justify-between gap-1">
              <CircleAlert className="w-3 h-3" />
              Problems
              <span className="text-[10px] text-muted-foreground">
                {aiFileProblems.file_name}
              </span>
              <span
                className="text-[10px] text-muted-foreground cursor-pointer"
                onClick={() => setAiFileProblems(null)}
              >
                <X className="w-[0.6rem] h-[0.6rem]" />
              </span>
            </div>
          )}
        </div>
        <Textarea
          ref={textareaRef}
          placeholder="Ask anything"
          className="resize-none border-none focus:ring-0 focus:outline-none focus:border-none focus:ring-offset-0 focus-visible:ring-0 focus-visible:ring-offset-0 min-h-8 p-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />

        <div className="flex justify-between items-center">
          <Select
            defaultValue={selectedModel}
            value={selectedModel}
            onValueChange={setSelectedModel}
          >
            <SelectTrigger className="w-fit border-none text-xs text-muted-foreground">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                {SUPPORTED_AI_MODELS.map((model) => (
                  <SelectItem key={model} value={model} className="text-xs">
                    {model}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
          <Button
            size="sm"
            variant="ghost"
            className="items-center flex space-x-2"
            onClick={handleSubmit}
            disabled={isLoading || !input.trim()}
          >
            {isLoading ? (
              <Loader2 className="w-3 h-3 animate-spin" />
            ) : (
              <>
                <CornerDownLeft className="w-3 h-3" />
                <div>Chat</div>
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
