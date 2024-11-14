import { type OpenedFile, useFiles } from "@/app/contexts/FilesContext";
import { Plus, X } from "lucide-react";
import type { RefObject } from "react";
import { Button } from "../ui/button";
import { ScrollArea, ScrollBar } from "../ui/scroll-area";
import { getIcon } from "./icons";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from "../ui/context-menu";
import { useCopyToClipboard } from "usehooks-ts";

export default function FileTabs({
  topBarRef,
  topBarWidth,
}: {
  topBarRef: RefObject<HTMLDivElement>;
  topBarWidth: number;
}) {
  const {
    openedFiles,
    activeFile,
    setActiveFile,
    closeFile,
    createNewFileTab,
    closeFilesToLeft,
    closeFilesToRight,
    closeAllOtherFiles,
    closeAllFiles,
  } = useFiles();
  const [copiedText, copy] = useCopyToClipboard();

  return (
    <div className="hover:cursor-pointer flex items-center space-x-0 py-0 bg-white dark:bg-black">
      <div
        className=""
        style={{
          maxWidth: topBarWidth ? topBarWidth - 50 : "100%",
        }}
      >
        <ScrollArea>
          <div className="flex h-9">
            {openedFiles.map((file: OpenedFile, index: number) => (
              <ContextMenu key={file.node.path}>
                <ContextMenuTrigger>
                  <div
                    key={file.node.path}
                    onClick={() => {
                      setActiveFile(file);
                    }}
                    className={`px-2 py-1 text-xs font-medium flex items-center space-x-1.5 group select-none text-muted-foreground dark:bg-zinc-800 ${file.node.path === activeFile?.node.path ? "text-black bg-white dark:bg-zinc-700 dark:text-zinc-100 border-b-white border border-t-black" : "border border-gray-200 dark:border-zinc-800"} ${index === 0 ? "border-l-0" : ""}`}
                  >
                    {getIcon(file.node)}
                    <div>{file.node.name}</div>
                    <div className="relative h-3 w-3 hover:bg-gray-200">
                      {file.isDirty && (
                        <div className="h-3 w-3 rounded-full bg-blue-300 group-hover:invisible" />
                      )}
                      <div
                        onClick={(e) => {
                          e.stopPropagation();
                          closeFile(file);
                        }}
                        className="rounded-full text-gray-400 w-3 h-3 flex justify-center items-center font-bold opacity-0 group-hover:opacity-100 absolute top-0 left-0"
                      >
                        <X className="h-5 w-5" />
                      </div>
                    </div>
                  </div>
                </ContextMenuTrigger>
                <ContextMenuContent>
                  <ContextMenuItem onClick={() => closeFile(file)}>
                    Close File
                  </ContextMenuItem>
                  <ContextMenuItem onClick={() => closeFilesToLeft(file)}>
                    Close Files to the Left
                  </ContextMenuItem>
                  <ContextMenuItem onClick={() => closeFilesToRight(file)}>
                    Close Files to the Right
                  </ContextMenuItem>
                  <ContextMenuItem onClick={() => closeAllOtherFiles(file)}>
                    Close All Other Files
                  </ContextMenuItem>
                  <ContextMenuItem onClick={() => closeAllFiles()}>
                    Close All Files
                  </ContextMenuItem>
                  <ContextMenuItem
                    onClick={() => {
                      copy(file.node.name);
                    }}
                  >
                    Copy File Name
                  </ContextMenuItem>
                </ContextMenuContent>
              </ContextMenu>
            ))}
          </div>
          <ScrollBar className="h-[0.45rem]" orientation="horizontal" />
        </ScrollArea>
      </div>
      <div>
        <Button
          onClick={() => createNewFileTab()}
          size="icon"
          variant="ghost"
          className="hover:bg-white"
        >
          <Plus className="h-3 w-3" />
        </Button>
      </div>
    </div>
  );
}
