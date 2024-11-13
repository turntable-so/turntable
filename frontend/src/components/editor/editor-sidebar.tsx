import {
  getMetabaseEmbedUrlForAsset,
  makeMetabaseAssetEmbeddable,
} from "@/app/actions/actions";
import { useFiles } from "@/app/contexts/FilesContext";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { useEffect, useRef, useState } from "react";
import { Tree } from "react-arborist";
import useResizeObserver from "use-resize-observer";
import ActionBar from "../ActionBar";
import EmbedAsset from "./embed-asset";
import Node from "./file-tree-node";
import { Separator } from "../ui/separator";
import { ScrollArea } from "../ui/scroll-area";
import { FolderOpen } from "lucide-react";
import { cn } from "@/lib/utils";


const SkeletonFileTree = () => {
  return (
    <div className="h-full flex flex-col animate-pulse">
      <div className="flex items-center space-x-2">
        <FolderOpen className="h-4 w-4" />
        <div className={cn("h-4 w-72 bg-gray-200 dark:bg-gray-800 rounded-sm")} />
      </div>
      {Array.from({ length: 30 }).map((_, index) => (
        <div key={index} className="flex items-center space-x-2 space-y-2">
          <FolderOpen className="h-4 w-4 invisible" />
          <div className={cn("h-4 w-72 bg-gray-200 dark:bg-gray-800 rounded-sm")} />
        </div>
      ))}
    </div>
  )
}

export default function EditorSidebar() {
  const {
    ref: treeContainerRef,
    width: treeWidth,
    height: treeHeight,
  } = useResizeObserver();
  const { files, activeFile, updateLoaderContent, openLoader, filesLoading } = useFiles();
  const treeRef = useRef<any>(null);

  const onCreate = async ({
    parentId,
    index,
    type,
  }: { parentId: string; index: number; type: string }) => { };
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

  const onActionBarSelectChange = (item: any) => {
    if (!item?.isSelectable) {
      return;
    }

    openLoader({ id: item.id, name: item.name });

    // Define the callback function
    const onEmbedded = () => {
      // Re-fetch and update content
      getMetabaseEmbedUrlForAsset(item.id).then((result) => {
        if (result.detail) {
          updateLoaderContent({
            path: item.id,
            content: `An error occurred: ${result.detail}`,
            newNodeType: "error",
          });
        } else if (!result.iframe_url) {
          updateLoaderContent({
            path: item.id,
            content: "Something went wrong. Please try again.",
            newNodeType: "error",
          });
        } else {
          updateLoaderContent({
            path: item.id,
            content: result.iframe_url,
            newNodeType: "url",
          });
        }
      });
    };

    // Fetch the embed URL
    getMetabaseEmbedUrlForAsset(item.id).then((result) => {
      if (result.detail === "NOT_EMBEDDED") {
        updateLoaderContent({
          path: item.id,
          content: <EmbedAsset assetId={item.id} onEmbedded={onEmbedded} />,
          newNodeType: "error",
        });
      } else if (result.detail) {
        updateLoaderContent({
          path: item.id,
          content: `An error occurred: ${result.detail}`,
          newNodeType: "error",
        });
      } else if (!result.iframe_url) {
        updateLoaderContent({
          path: item.id,
          content: "Something went wrong. Please try again.",
          newNodeType: "error",
        });
      } else {
        updateLoaderContent({
          path: item.id,
          content: result.iframe_url,
          newNodeType: "url",
        });
      }
    });
  };

  return (
    <div className="h-full flex flex-col bg-muted">
      <ResizablePanelGroup direction="vertical" className="py-2">
        <ResizablePanel defaultSize={75} minSize={30} maxSize={75}>
          <div className="h-full w-full px-2">
            <div className="flex items-center space-x-2">
              <div className="px-1 text-black text-sm font-medium">Files</div>
            </div>
            <div className="pt-2 h-full px-1" ref={treeContainerRef}>
              {filesLoading ? <SkeletonFileTree /> : (
                <Tree
                  scrollTo={activeFile?.node.path}
                  selection={activeFile?.node.path}
                  height={treeHeight}
                  width={treeWidth}
                  data={files}
                  openByDefault={false}
                  indent={12}
                  // opens the root by default
                  initialOpenState={{
                    '.': true,
                  }}
                  ref={treeRef}
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
              )}
            </div>
          </div>
        </ResizablePanel>
        {/*<div className="px-2 pb-2">*/}
        {/*  <ResizableHandle className="h-10" withHandle />*/}
        {/*</div>*/}
        {/*<ResizablePanel defaultSize={25} minSize={25} maxSize={70}>*/}
        {/*  <div className="h-full w-full">*/}
        {/*    <div className="flex items-center space-x-2 px-2">*/}
        {/*      <div className="px-1 text-black text-sm font-medium">*/}
        {/*        Resources*/}
        {/*      </div>*/}
        {/*    </div>*/}
        {/*    <ActionBar*/}
        {/*      context="EDITOR"*/}
        {/*      onSelectChange={onActionBarSelectChange}*/}
        {/*    />*/}
        {/*  </div>*/}
        {/*</ResizablePanel>*/}
      </ResizablePanelGroup>
    </div >
  );
}
