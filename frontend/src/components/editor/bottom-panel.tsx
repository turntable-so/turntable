import { useFiles } from "@/app/contexts/FilesContext";
import { useLineage } from "@/app/contexts/LineageContext";
import { useBottomPanelTabs } from "@/components/editor/use-bottom-panel-tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { AgGridReact } from "ag-grid-react";
import {
  Loader2,
  Network,
  Play,
  RefreshCcw,
  Table as TableIcon,
  Terminal as TerminalIcon,
} from "lucide-react";
import { useEffect } from "react";
import { Fragment } from "react";
import { ErrorBoundary } from "react-error-boundary";
import { Panel, PanelResizeHandle } from "react-resizable-panels";
import useResizeObserver from "use-resize-observer";
import { LineageView } from "../lineage/LineageView";
import { Button } from "../ui/button";
import { Tabs, TabsList, TabsTrigger } from "../ui/tabs";
import CommandPanel from "./command-panel";
import { useParams } from "next/navigation";

const SkeletonLoadingTable = () => {
  return (
    <div className="w-full flex items-center justify-center">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[100px]">
              <div className="animate-pulse h-4 bg-gray-200 rounded"></div>
            </TableHead>
            <TableHead>
              <div className="animate-pulse h-4 bg-gray-200 rounded"></div>
            </TableHead>
            <TableHead>
              <div className="animate-pulse h-4 bg-gray-200 rounded"></div>
            </TableHead>
            <TableHead className="text-right">
              <div className="animate-pulse h-4 bg-gray-200 rounded"></div>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {Array.from({ length: 20 }).map((_, i) => (
            <TableRow key={i}>
              <TableCell className="">
                <div className="animate-pulse h-4 bg-gray-200 rounded"></div>
              </TableCell>
              <TableCell className="">
                <div className="animate-pulse h-4 bg-gray-200 rounded"></div>
              </TableCell>
              <TableCell className="">
                <div className="animate-pulse h-4 bg-gray-200 rounded"></div>
              </TableCell>
              <TableCell className="">
                <div className="animate-pulse h-4 bg-gray-200 rounded"></div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default function BottomPanel({
  rowData,
  gridRef,
  colDefs,
  runQueryPreview,
  isLoading: isQueryLoading,
  queryPreviewError,
}: {
  rowData: any;
  gridRef: any;
  colDefs: any;
  runQueryPreview: any;
  isLoading: boolean;
  queryPreviewError: string | null;
}) {
  const { fetchFileBasedLineage, lineageData } = useLineage();
  const { activeFile, branchId } = useFiles();
  const [activeTab, setActiveTab] = useBottomPanelTabs({
    branchId: branchId || "",
  });

  useEffect(() => {
    if (branchId && activeFile && activeFile.node.path.endsWith(".sql")) {
      if (!lineageData[activeFile.node.path]) {
        fetchFileBasedLineage(activeFile.node.path, branchId);
      }
    }
  }, [activeFile, activeTab, fetchFileBasedLineage, branchId]);

  const { ref: bottomPanelRef, height: bottomPanelHeight } =
    useResizeObserver();

  return (
    <Fragment>
      <PanelResizeHandle className="h-1 bg-gray hover:bg-gray-300 hover:cursor-col-resize  transition-colors" />
      <div className="h-10 bg-muted/50 border-t-2 flex justify-between items-center">
        <Tabs
          value={activeTab}
          onValueChange={(value) =>
            setActiveTab(value as "lineage" | "results" | "command")
          }
          className="text-sm"
        >
          <TabsList>
            <TabsTrigger value="results">
              <TableIcon className="h-4 w-4 mr-2" />
              Preview
            </TabsTrigger>
            <TabsTrigger value="lineage">
              {lineageData[activeFile?.node.path || ""]?.isLoading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Network className="h-4 w-4 mr-2" />
              )}
              Lineage
            </TabsTrigger>

            <TabsTrigger value="command">
              <TerminalIcon className="h-4 w-4 mr-2" />
              Command
            </TabsTrigger>
          </TabsList>
        </Tabs>
        <div className="mr-2">
          {activeTab === "results" && (
            <Button
              size="sm"
              onClick={runQueryPreview}
              disabled={isQueryLoading}
              variant="outline"
            >
              {isQueryLoading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Play className="h-4 w-4 mr-2" />
              )}
              Preview Query
            </Button>
          )}
          {activeTab === "lineage" && (
            <Button
              size="sm"
              onClick={() => fetchFileBasedLineage(activeFile?.node.path || "")}
              disabled={lineageData[activeFile?.node.path || ""]?.isLoading}
              variant="outline"
            >
              {lineageData[activeFile?.node.path || ""]?.isLoading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <RefreshCcw className="h-4 w-4 mr-2" />
              )}
              Refresh
            </Button>
          )}
        </div>
      </div>
      <Panel
        defaultSize={40}
        className="border-t flex items-center justify-center"
      >
        <div
          className="flex flex-col w-full h-full flex-grow-1"
          ref={bottomPanelRef}
        >
          {activeTab === "results" &&
            (() => {
              switch (true) {
                case isQueryLoading:
                  return <SkeletonLoadingTable />;
                case !!queryPreviewError:
                  return (
                    <div
                      style={{
                        height: bottomPanelHeight,
                      }}
                      className="overflow-y-scroll  p-6 "
                    >
                      <div className=" text-red-500 text-sm">
                        {queryPreviewError}
                      </div>
                      <div className="h-24" />
                    </div>
                  );
                default:
                  return (
                    <AgGridReact
                      className="ag-theme-custom"
                      ref={gridRef}
                      suppressRowHoverHighlight={true}
                      columnHoverHighlight={true}
                      rowData={rowData}
                      pagination={true}
                      // @ts-ignore
                      columnDefs={colDefs}
                    />
                  );
              }
            })()}
          {activeTab === "lineage" && (
            <div className="h-full">
              <ErrorBoundary
                FallbackComponent={() => <div>Something went wrong</div>}
              >
                <>
                  {lineageData &&
                    lineageData[activeFile?.node.path || ""] &&
                    lineageData[activeFile?.node.path || ""].isLoading && (
                      <div
                        className="w-full bg-gray-200 flex items-center justify-center"
                        style={{ height: bottomPanelHeight }}
                      >
                        <Loader2 className="h-6 w-6 animate-spin opacity-50" />
                      </div>
                    )}
                  {lineageData &&
                    lineageData[activeFile?.node.path || ""] &&
                    lineageData[activeFile?.node.path || ""].data && (
                      <LineageView
                        key={activeFile?.node.path}
                        lineage={
                          lineageData[activeFile?.node.path || ""].data.lineage
                        }
                        rootAsset={
                          lineageData[activeFile?.node.path || ""].data
                            .root_asset
                        }
                        style={{ height: bottomPanelHeight }}
                      />
                    )}
                  {lineageData &&
                    lineageData[activeFile?.node.path || ""] &&
                    lineageData[activeFile?.node.path || ""].error && (
                      <div
                        className="w-full bg-gray-200 flex items-center justify-center"
                        style={{ height: bottomPanelHeight }}
                      >
                        <div className="text-red-500 text-sm">
                          {lineageData[activeFile?.node.path || ""].error}
                        </div>
                      </div>
                    )}
                </>
              </ErrorBoundary>
            </div>
          )}
          {activeTab === "command" && (
            <CommandPanel bottomPanelHeight={bottomPanelHeight} />
          )}
        </div>
      </Panel>
    </Fragment>
  );
}
