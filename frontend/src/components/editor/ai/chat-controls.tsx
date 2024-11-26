import type { FileNode } from "@/app/contexts/FilesContext";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { CornerDownLeft, Loader2, Plus } from "lucide-react";
import type React from "react";
import { type Dispatch, type SetStateAction, useState } from "react";
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
import FileExplorer from "./file-explorer";

interface ChatControlsProps {
  input: string;
  setInput: (value: string) => void;
  isLoading: boolean;
  handleSubmit: (e: React.FormEvent) => void;
  activeFile: any;
  lineageData: any;
  contextFiles: FileNode[];
  setContextFiles: Dispatch<SetStateAction<FileNode[]>>;
}

export default function ChatControls({
  input,
  setInput,
  isLoading,
  handleSubmit,
  activeFile,
  lineageData,
  contextFiles,
  setContextFiles,
}: ChatControlsProps) {
  const [isFileExplorerOpen, setIsFileExplorerOpen] = useState(false);
  const numberOfLineageFiles = lineageData?.data?.assets?.length;

  const handleRemoveContextFile = (file: FileNode) => {
    setContextFiles((prev) => prev.filter((f) => f.path !== file.path));
  };

  return (
    <div className="flex flex-col bg-background rounded-md p-2 gap-2 relative">
      <div className="flex gap-1 flex-wrap">
        <div
          className="hover:bg-muted rounded-md p-0.5 cursor-pointer border flex items-center justify-center relative"
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
        <div className="bg-muted/50 rounded-md p-1 text-xs">
          {activeFile?.node.name}{" "}
          <span className="text-[10px] text-muted-foreground">
            Current file
          </span>
        </div>

        {numberOfLineageFiles > 0 ? (
          <Tooltip delayDuration={100}>
            <TooltipTrigger asChild>
              <div className="bg-muted/50 rounded-md p-1 text-xs">
                {numberOfLineageFiles}{" "}
                <span className="text-[10px] text-muted-foreground">
                  models from lineage
                </span>
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <p>{lineageData?.data?.assets?.map((asset: any) => asset.name).join(", ")}</p>
            </TooltipContent>
          </Tooltip>
        ) : null}

        {contextFiles.map((file) => (
          <Tooltip key={file.path} delayDuration={100}>
            <TooltipTrigger asChild>
              <div
                className="bg-muted/50 rounded-md p-1 text-xs cursor-pointer"
                onClick={() => handleRemoveContextFile(file)}
              >
                {file.name}{" "}
                <span className="text-[10px] text-muted-foreground">File</span>
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <p>Click to remove</p>
            </TooltipContent>
          </Tooltip>
        ))}
      </div>
      <Textarea
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
        <Select defaultValue="claude-3.5-sonnet">
          <SelectTrigger className="w-fit border-none text-xs text-muted-foreground">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectItem value="claude-3.5-sonnet">
                claude-3.5-sonnet
              </SelectItem>
              <SelectItem value="gpt-4o">gpt-4o</SelectItem>
              <SelectItem value="o1-mini">o1-mini</SelectItem>
              <SelectItem value="o1-preview">o1-preview</SelectItem>
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
  );
}
