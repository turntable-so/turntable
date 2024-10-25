import { useFiles } from "@/app/contexts/FilesContext";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { ChevronDown } from "lucide-react";
import { useEffect, useRef } from "react";
import { Tree } from "react-arborist";
import useResizeObserver from "use-resize-observer";
import ActionBar from "../ActionBar";
import { Input } from "../ui/input";
import { ScrollArea } from "../ui/scroll-area";
import Node from "./file-tree-node";
export default function EditorSidebar() {
  const {
    ref: treeContainerRef,
    width: treeWidth,
    height: treeHeight,
  } = useResizeObserver();
  const { files, activeFile } = useFiles();
  const treeRef = useRef<any>(null);

  const onCreate = async ({
    parentId,
    index,
    type,
  }: { parentId: string; index: number; type: string }) => {};
  const onRename = ({ id, name }: { id: string; name: string }) => {
    console.log("renaming!", { id, name });
  };
  // noop
  const onMove = ({
    dragIds,
    parentId,
    index,
  }: { dragIds: string[]; parentId: string; index: number }) => {
    console.log("moving!", { dragIds, parentId, index });
  };

  const onDelete = ({ ids }: { ids: string[] }) => {
    console.log("deleting!", { ids });
  };

  useEffect(() => {
    if (files.length > 0) {
    }
  }, [files]);

  return (
    <div className="h-full flex flex-col bg-muted">
      <ResizablePanelGroup direction="vertical" className="py-2">
        <ResizablePanel defaultSize={50} minSize={30} maxSize={70}>
          <div className="h-full w-full px-2">
            <div className="flex items-center space-x-2">
              <div className="px-1 text-black text-sm font-medium">Files </div>
            </div>
            <div className="pt-2 h-full px-1" ref={treeContainerRef}>
              <Tree
                selection={activeFile?.node.path}
                height={treeHeight}
                width={treeWidth}
                data={files}
                openByDefault={false}
                indent={12}
                ref={treeRef}
                openNodes={[files[0]?.path]}
                // @ts-ignore
                onCreate={onCreate}
                // @ts-ignore
                onRename={onRename}
                // @ts-ignore
                onMove={onMove}
                // @ts-ignore
                onDelete={onDelete}
              >
                {Node as any}
              </Tree>
            </div>
          </div>
        </ResizablePanel>
        <div className="px-2 pb-2">
          <ResizableHandle className="h-10" withHandle />
        </div>
        <ResizablePanel defaultSize={70} minSize={30} maxSize={70}>
          <div className="h-full w-full">
            <div className="flex items-center space-x-2 px-2">
              <div className="px-1 text-black text-sm font-medium">
                Resources
              </div>
            </div>
            {/* <ScrollArea className='h-full z-50'>
                            <ActionBar key={'pls_remove'} context={'NOTEBOOK'} />
                        </ScrollArea> */}
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}
