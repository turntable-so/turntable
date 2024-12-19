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
import { useEffect, useRef, useState } from "react";
import {
  type ImperativePanelHandle,
  Panel,
  PanelGroup,
  PanelResizeHandle,
} from "react-resizable-panels";
import useResizeObserver from "use-resize-observer";
import { useFiles } from "../../contexts/FilesContext";
import { useLayoutContext } from "../../contexts/LayoutContext";

function EditorPageContent() {
  const {
    ref: topBarRef,
    width: topBarWidth,
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
    sidebarLeftWidth,
    sidebarRightWidth,
    bottomPanelWidth,
    setSidebarLeftWidth,
    setSidebarRightWidth,
    setBottomPanelWidth,
    isSidebarLeftCollapsed,
    isSidebarRightCollapsed,
    isBottomPanelCollapsed,
  } = useLayoutContext();

  const gridRef = useRef<AgGridReact>(null);
  const leftPanelRef = useRef<ImperativePanelHandle>(null);
  const rightPanelRef = useRef<ImperativePanelHandle>(null);

  const treeRef = useRef<any>(null);
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const [filesearchQuery, setFilesearchQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const pathname = usePathname();
  const {
    fetchFiles,
    fetchBranch,
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
              setSidebarRightWidth(isSidebarRightCollapsed ? 20 : 0);
            } else {
              setSidebarLeftWidth(isSidebarLeftCollapsed ? 20 : 0);
            }
            break;
          case "p":
            event.preventDefault();
            searchInputRef.current?.focus();
            break;
          case "j":
            event.preventDefault();
            setBottomPanelWidth(isBottomPanelCollapsed ? 20 : 0);
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
            setSelectedIndex((prevIndex) => prevIndex + 1);
            break;
          case "Enter":
            event.preventDefault();
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
    sidebarLeftWidth,
    sidebarRightWidth,
    bottomPanelWidth,
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

  useEffect(() => {
    const panel = leftPanelRef.current;
    if (!panel) return;
    if (sidebarLeftWidth === 0) {
      panel.collapse();
    } else {
      panel.expand();
      panel.resize(sidebarLeftWidth);
    }
  }, [sidebarLeftWidth]);

  useEffect(() => {
    const panel = rightPanelRef.current;
    if (!panel) return;
    if (sidebarRightWidth === 0) {
      panel.collapse();
    } else {
      panel.expand();
      panel.resize(sidebarRightWidth);
    }
  }, [sidebarRightWidth]);

  return (
    <div className="flex flex-col h-screen">
      <EditorTopBar />
      <PanelGroup
        direction="horizontal"
        className="h-fit"
        onLayout={(sizes) => {
          setSidebarLeftWidth(sizes[0]);
          setSidebarRightWidth(sizes[2]);
        }}
      >
        <Panel
          ref={leftPanelRef}
          collapsible
          minSize={15}
          maxSize={30}
          defaultSize={sidebarLeftWidth}
          onResize={setSidebarLeftWidth}
          collapsedSize={0}
          className="border-r text-gray-600 dark:border-zinc-700"
        >
          <EditorSidebar />
        </Panel>
        <PanelResizeHandle className="bg-transparent transition-colors" />
        <Panel>
          <div className="h-full" ref={topBarRef}>
            <FileTabs
              topBarRef={topBarRef as any}
              topBarWidth={(topBarWidth ?? 0) + 14}
            />
            <div className="w-full h-full">
              <PanelGroup direction="vertical" className="h-fit">
                <Panel className="h-full relative z-0">
                  <EditorContent containerWidth={topBarWidth ?? 0} />
                </Panel>
                {bottomPanelWidth > 0 && (
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
        <PanelResizeHandle className="border-l w-1 bg-transparent hover:bg-gray-300 hover:cursor-col-resize transition-colors" />
        <Panel
          ref={rightPanelRef}
          collapsible
          minSize={25}
          maxSize={60}
          defaultSize={sidebarRightWidth}
          onResize={setSidebarRightWidth}
          collapsedSize={0}
        >
          <div className="bg-muted h-full p-4 flex justify-center">
            <AiSidebarChat />
          </div>
        </Panel>
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
