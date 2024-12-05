import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-balham.css";
import "./ag-grid-custom-theme.css";

import { useFiles } from "@/app/contexts/FilesContext";
import { useBottomPanelTabs } from "@/components/editor/use-bottom-panel-tabs";
import {
  CircleAlertIcon,
  DatabaseZap,
  Loader2,
  Network,
  Play,
  RefreshCcw,
  Table as TableIcon,
  Terminal as TerminalIcon,
} from "lucide-react";
import { Fragment, useContext } from "react";
import { ErrorBoundary } from "react-error-boundary";
import { Panel, PanelResizeHandle } from "react-resizable-panels";
import useResizeObserver from "use-resize-observer";
import {
  LineageView,
  LineageViewContext,
} from "../../app/contexts/LineageView";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Label } from "../ui/label";
import { Switch } from "../ui/switch";
import { Tabs, TabsList, TabsTrigger } from "../ui/tabs";
import { Tooltip, TooltipContent, TooltipTrigger } from "../ui/tooltip";
import CustomEditor from "./CustomEditor";
import CommandPanel from "./command-panel";
import CommandPanelActionBtn from "./command-panel/command-panel-action-btn";
import ErrorMessage from "./error-message";
import PreviewPanel from "./preview-panel/preview-panel";
import ProblemsPanel from "./problems-panel/problems-panel";

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
  const { setLineageOptionsAndRefetch, lineageOptions } =
    useContext(LineageViewContext);
  const { lineageData } = useFiles();

  const fetchFileBasedLineage = () => {
    setLineageOptionsAndRefetch(lineageOptions, {
      shouldCheckLineageData: false,
    });
  };

  const {
    activeFile,
    branchId,
    problems,
    compileActiveFile,
    compiledSql,
    isCompiling,
    compileError,
    isQueryPreviewLoading,
    isSqlFile,
  } = useFiles();

  const [activeTab, setActiveTab] = useBottomPanelTabs({
    branchId: branchId || "",
  });

  const {
    ref: bottomPanelRef,
    height: bottomPanelHeight,
    width: bottomPanelWidth,
  } = useResizeObserver();

  const showPreviewQueryButton =
    activeTab === "results" &&
    activeFile?.node.type === "file" &&
    activeFile.node.name.endsWith(".sql");

  return (
    <Fragment>
      <PanelResizeHandle className="h-1 hover:bg-gray-300 dark:hover:bg-zinc-700 hover:cursor-col-resize transition-colors" />
      <div className="h-10 bg-muted/50 dark:bg-zinc-800 border-t-2 flex justify-between items-center">
        <Tabs
          value={activeTab}
          onValueChange={(value) =>
            setActiveTab(value as "lineage" | "results" | "command" | "compile")
          }
          className="text-sm"
        >
          <TabsList>
            <TabsTrigger value="results">
              {isQueryPreviewLoading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <TableIcon className="h-4 w-4 mr-2" />
              )}
              Preview
            </TabsTrigger>
            <TabsTrigger value="compile">
              {isCompiling ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <DatabaseZap className="h-4 w-4 mr-2" />
              )}
              Compile
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

            <TabsTrigger value="problems">
              <CircleAlertIcon className="h-4 w-4 mr-2" />
              Problems
              {isSqlFile ? (
                problems.loading ? (
                  <Loader2 className="h-4 w-4 ml-2 animate-spin" />
                ) : (
                  problems.data.length > 0 && (
                    <Badge className="ml-2 font-mono" variant={"outline"}>
                      {problems.data.length}
                    </Badge>
                  )
                )
              ) : null}
            </TabsTrigger>
          </TabsList>
        </Tabs>
        <div className="mr-2">
          {showPreviewQueryButton && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  size="sm"
                  onClick={() => runQueryPreview()}
                  disabled={isQueryLoading}
                  variant="outline"
                >
                  {isQueryLoading ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Play className="h-4 w-4 mr-2" />
                  )}
                  Preview
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Preview Query (⌘ + Enter)</p>
              </TooltipContent>
            </Tooltip>
          )}
          {activeTab === "compile" && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  size="sm"
                  onClick={compileActiveFile}
                  disabled={isCompiling}
                  variant="outline"
                >
                  {isCompiling ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Play className="h-4 w-4 mr-2" />
                  )}
                  Compile
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Compile (⌘ + Shift + Enter)</p>
              </TooltipContent>
            </Tooltip>
          )}
          {activeTab === "lineage" && (
            <div className="flex items-center justify-center gap-2">
              <div className="flex items-center space-x-2">
                <Switch
                  id="asset-only"
                  checked={
                    !lineageData[activeFile?.node.path || ""]?.showColumns
                  }
                  onCheckedChange={(checked) => {
                    setLineageOptionsAndRefetch(
                      {
                        ...lineageOptions,
                        asset_only: !checked,
                      },
                      { shouldCheckLineageData: false },
                    );
                  }}
                />
                <Label htmlFor="asset-only" className="text-muted-foreground">
                  Show Columns
                </Label>
              </div>
              <Button
                size="sm"
                onClick={fetchFileBasedLineage}
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
            </div>
          )}
          {activeTab === "command" && <CommandPanelActionBtn />}
        </div>
      </div>
      <Panel
        defaultSize={40}
        className="border-t flex items-center justify-center dark:bg-zinc-950"
      >
        <div
          className="flex flex-col w-full h-full flex-grow-1 dark:bg-black"
          ref={bottomPanelRef}
        >
          {activeTab === "results" && (
            <PreviewPanel
              isQueryLoading={isQueryLoading}
              queryPreviewError={queryPreviewError}
              bottomPanelHeight={bottomPanelHeight}
              gridRef={gridRef}
              rowData={rowData}
              colDefs={colDefs}
            />
          )}
          {activeTab === "lineage" && (
            <div className="h-full">
              <ErrorBoundary
                FallbackComponent={() => <div>Something went wrong</div>}
              >
                <>
                  {lineageData?.[activeFile?.node.path || ""] &&
                    lineageData[activeFile?.node.path || ""].isLoading && (
                      <div
                        className="w-full bg-gray-200 dark:bg-black flex items-center justify-center"
                        style={{ height: bottomPanelHeight }}
                      >
                        <Loader2 className="h-6 w-6 animate-spin opacity-50" />
                      </div>
                    )}
                  {lineageData?.[activeFile?.node.path || ""] &&
                    lineageData[activeFile?.node.path || ""].data && (
                      <LineageView
                        style={{ height: (bottomPanelHeight ?? 0) - 28 }}
                      />
                    )}
                  {lineageData?.[activeFile?.node.path || ""] &&
                    lineageData[activeFile?.node.path || ""].error && (
                      <ErrorMessage
                        error={lineageData[activeFile?.node.path || ""].error}
                      />
                    )}
                </>
              </ErrorBoundary>
            </div>
          )}
          {activeTab === "command" && (
            <CommandPanel bottomPanelHeight={bottomPanelHeight} />
          )}
          {activeTab === "problems" && <ProblemsPanel />}
          {activeTab === "compile" && (
            <div className="h-full w-full">
              {compileError ? (
                <ErrorMessage error={compileError} />
              ) : (
                <CustomEditor
                  key={compiledSql}
                  value={compiledSql || ""}
                  language="sql"
                  options={{
                    readOnly: true,
                    minimap: { enabled: false },
                    scrollbar: {
                      vertical: "visible",
                      horizontal: "visible",
                      verticalScrollbarSize: 8,
                      horizontalScrollbarSize: 8,
                      verticalSliderSize: 8,
                      horizontalSliderSize: 8,
                    },
                    lineNumbers: "on",
                    wordWrap: "on",
                    fontSize: 14,
                    lineNumbersMinChars: 3,
                    renderLineHighlight: "none",
                  }}
                  height={bottomPanelHeight}
                  width={bottomPanelWidth}
                />
              )}
            </div>
          )}
        </div>
      </Panel>
    </Fragment>
  );
}
