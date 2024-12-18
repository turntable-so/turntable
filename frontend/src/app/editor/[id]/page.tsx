"use client";

import AiSidebarChat from "@/components/editor/ai/ai-sidebar";
import BottomPanel from "@/components/editor/bottom-panel";
import ConfirmSaveDialog from "@/components/editor/dialogs/confirm-save-dialog";
import EditorContent from "@/components/editor/editor-content";
import EditorSidebar from "@/components/editor/editor-sidebar";
import EditorTopBar from "@/components/editor/editor-top-bar";
import FileTabs from "@/components/editor/file-tabs";
import type { AgGridReact } from "ag-grid-react";
import { usePathname } from "next/navigation";
import { Fragment, useEffect, useRef, useState } from "react";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import useResizeObserver from "use-resize-observer";
import { useFiles } from "../../contexts/FilesContext";
import { useLayoutContext } from "../../contexts/LayoutContext";

function EditorPageContent() {
  const [leftWidth, setLeftWidth] = useState(20);
  const [rightWidth, setRightWidth] = useState(20);
  const {
    ref: topBarRef,
    width: topBarWidth,
    height: topBarHeight,
  } = useResizeObserver();

  const {
    files,
    activeFile,
    queryPreview,
    queryPreviewError,
    isQueryPreviewLoading,
    setIsQueryPreviewLoading,
    saveFile,
    queryPreviewData,
    setQueryPreviewData,
  } = useFiles();

  const {
    sidebarLeftShown,
    sidebarRightShown,
    bottomPanelShown,
    setSidebarLeftShown,
    setSidebarRightShown,
    setBottomPanelShown,
  } = useLayoutContext();

  const gridRef = useRef<AgGridReact>(null);

  const treeRef = useRef<any>(null);
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const [filesearchQuery, setFilesearchQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const pathname = usePathname();
  const {
    fetchFiles,
    fetchBranch,
    branchName,
    branchId,
    isCloned,
    cloneBranch,
    compileActiveFile,
    runQueryPreview,
  } = useFiles();

  useEffect(() => {
    if (branchId && isCloned) {
      fetchFiles();
    }
    if (branchId && !isCloned) {
      cloneBranch(branchId);
    }
  }, [branchId, isCloned]);

  useEffect(() => {
    if (pathname?.includes("/editor/")) {
      const id = pathname.split("/").slice(-1)[0];
      if (id && id.length > 0) {
        fetchBranch(id);
      }
    }
  }, [pathname]);

  useEffect(() => {
    if (treeRef.current) {
      const rootNode = treeRef.current.root;
      if (rootNode && rootNode.children.length > 0) {
        rootNode.children[0].open();
      }
    }
  }, [files]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.metaKey) {
        switch (event.key.toLowerCase()) {
          case "s":
            event.preventDefault();
            if (activeFile?.node.path) {
              saveFile(activeFile.node.path, activeFile.content as string);
            }
            break;
          case "b":
            event.preventDefault();
            if (event.shiftKey) {
              setSidebarRightShown(!sidebarRightShown);
            } else {
              setSidebarLeftShown(!sidebarLeftShown);
            }
            break;
          case "p":
            event.preventDefault();
            searchInputRef.current?.focus();
            break;
          case "j":
            event.preventDefault();
            setBottomPanelShown(!bottomPanelShown);
            break;
          case "enter":
            event.preventDefault();
            if (event.shiftKey) {
              compileActiveFile(activeFile?.node.name || "");
            } else {
              runQueryPreview();
            }
            break;
        }
      }

      if (isSearchFocused) {
        switch (event.key) {
          case "ArrowUp":
            event.preventDefault();
            setSelectedIndex((prevIndex) => Math.max(0, prevIndex - 1));
            break;
          case "ArrowDown":
            event.preventDefault();
            setSelectedIndex((prevIndex) => prevIndex + 1); // You might want to add a max limit based on search results
            break;
          case "Enter":
            event.preventDefault();
            // Handle file selection here
            setIsSearchFocused(false);
            setFilesearchQuery("");
            break;
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [
    sidebarLeftShown,
    sidebarRightShown,
    bottomPanelShown,
    isSearchFocused,
    selectedIndex,
    activeFile,
    saveFile,
    runQueryPreview,
    compileActiveFile,
  ]);

  const getTablefromSignedUrl = async (signedUrl: string, fileName: string) => {
    const response = await fetch(signedUrl);
    if (response.ok) {
      const table = await response.json();
      const defs = Object.keys(table.data[0]).map((key) => ({
        field: key,
        headerName: key,
        // type: [getColumnType(table.column_types[key])],
        // cellDataType: getColumnType(table.column_types[key]),
        editable: false,
        valueGetter: (p: any) => {
          if (p.colDef.cellDataType === "date") {
            return new Date(p.data[key]);
          }
          return p.data[key];
        },
        cellClass: "p-0",
      }));
      setQueryPreviewData({
        rows: table.data,
        cols: defs,
        file_name: fileName,
      });
    }
    setIsQueryPreviewLoading(false);
  };

  useEffect(() => {
    const fetchQueryPreview = async () => {
      if (queryPreview?.signed_url) {
        getTablefromSignedUrl(
          queryPreview.signed_url,
          activeFile?.node.name || "",
        );
      }
    };
    fetchQueryPreview();
  }, [queryPreview?.signed_url]);

  return (
    <div className="flex flex-col h-screen">
      <EditorTopBar />
      <PanelGroup direction="horizontal" className="h-fit">
        {sidebarLeftShown && (
          <Panel
            defaultSize={leftWidth}
            minSize={15}
            maxSize={30}
            onResize={setLeftWidth}
            className="border-r text-gray-600 dark:border-zinc-700"
          >
            <EditorSidebar />
          </Panel>
        )}
        {/* <Panel defaultSize={leftWidth} minSize={15} maxSize={30} onResize={setLeftWidth} className='border-r bg-muted/50 text-gray-600'>
                    <Tabs defaultValue="files" className="h-full">
                        <div
                            className={cn(
                                "flex h-[52px] items-center justify-center",
                                "h-[52px]"
                            )}
                        >
                            <TabsList className="grid w-full grid-cols-2 mx-4">
                                <TabsTrigger value="files" className="flex items-center justify-center">
                                    <File className="w-4 h-4 mr-2" />
                                    Files
                                </TabsTrigger>
                                <TabsTrigger value="branch" className="flex items-center justify-center">
                                    <GitBranch className="w-4 h-4 mr-2" />
                                    Branch
                                </TabsTrigger>
                            </TabsList>
                        </div>
                        <Separator />
                        <TabsContent value="files" className='h-full px-2'>
                            <div className="h-full" ref={treeContainerRef}>
                                <Tree
                                    selection={activeFile?.node.path}
                                    height={treeHeight}
                                    width={treeWidth}
                                    data={files}
                                    openByDefault={false}
                                    indent={12}
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
                            </div>
                        </TabsContent>
                        <TabsContent value="branch">Branches</TabsContent>
                    </Tabs>
                </Panel> */}
        <PanelResizeHandle className="bg-transparent transition-colors" />
        <Panel>
          <div className="h-full" ref={topBarRef}>
            <FileTabs
              topBarRef={topBarRef as any}
              topBarWidth={topBarWidth + 14 as number}
            />
            <div className="w-full h-full">
              <PanelGroup direction="vertical" className="h-fit">
                <Panel className="h-full relative z-0">
                  <EditorContent containerWidth={topBarWidth as number} />
                </Panel>
                {bottomPanelShown && (
                  <BottomPanel
                    rowData={queryPreviewData?.rows}
                    gridRef={gridRef}
                    colDefs={queryPreviewData?.cols}
                    runQueryPreview={runQueryPreview}
                    queryPreviewError={queryPreviewError}
                    isLoading={isQueryPreviewLoading}
                  />
                )}
              </PanelGroup>
            </div>
          </div>
        </Panel>
        {sidebarRightShown && (
          <Fragment>
            <PanelResizeHandle className="border-l w-1 bg-transparent hover:bg-gray-300 hover:cursor-col-resize transition-colors" />
            <Panel
              defaultSize={rightWidth}
              minSize={25}
              maxSize={60}
              onResize={setRightWidth}
            >
              <div className="bg-muted h-full p-4 flex justify-center">
                <AiSidebarChat />
              </div>
            </Panel>
          </Fragment>
        )}
      </PanelGroup>
    </div>
  );
}

export default function EditorPage() {
  return (
    <div>
      <EditorPageContent />
      <ConfirmSaveDialog />
    </div>
  );
}
