import { type OpenedFile, useFiles } from "@/app/contexts/FilesContext";
import { Plus, X } from "lucide-react";
import type { RefObject } from "react";
import { Button } from "../ui/button";
import { ScrollArea, ScrollBar } from "../ui/scroll-area";

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
  } = useFiles();

  return (
    <div className="hover:cursor-pointer flex items-center space-x-0 py-0 bg-white">
      <div
        className=""
        style={{
          maxWidth: topBarWidth ? topBarWidth - 50 : "100%",
        }}
      >
        <ScrollArea>
          <div className="flex h-9">
            {openedFiles.map((file: OpenedFile, index: number) => (
              <div
                key={file.node.path}
                onClick={() => {
                  setActiveFile(file);
                }}
                className={`px-2 py-1 text-xs font-medium flex items-center space-x-2 group select-none text-muted-foreground ${file.node.path === activeFile?.node.path ? "text-black bg-white border-b-white border border-t-black" : "border border-gray-200"} ${index === 0 ? "border-l-0" : ""}`}
              >
                <div>{file.node.name}</div>
                <div className="relative h-3 w-3 hover:bg-gray-200">
                  {file.isDirty && (
                    <div className="h-3 w-3 rounded-full bg-blue-300 group-hover:invisible"></div>
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
