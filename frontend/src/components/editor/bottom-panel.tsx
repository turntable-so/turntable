import { useEffect, useState } from "react";
import { AgGridReact } from "ag-grid-react";
import { Loader2, Network, Play, RefreshCcw, Table } from "lucide-react";
import { Button } from "../ui/button";
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { Fragment } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs"
import LineagePreview from "../lineage/LineagePreview";
import { useLineage } from "@/app/contexts/LineageContext";
import { ErrorBoundary } from "react-error-boundary";
import { useFiles } from "@/app/contexts/FilesContext";
import { LineageView } from "../lineage/LineageView";

export default function BottomPanel({ rowData, gridRef, colDefs, runQueryPreview, isLoading: isQueryLoading }: {
    rowData: any,
    gridRef: any,
    colDefs: any,
    runQueryPreview: any,
}) {
    const [activeTab, setActiveTab] = useState("lineage");

    const { fetchFileBasedLineage, lineageData } = useLineage()
    const { activeFile } = useFiles()

    useEffect(() => {
        if (activeFile && activeTab === "lineage" && activeFile.node.path.endsWith(".sql")) {
            if (!lineageData[activeFile.node.path]) {
                fetchFileBasedLineage(activeFile.node.path)
            }
        }
    }, [activeFile, activeTab, fetchFileBasedLineage])


    console.log({ lineageData })



    return (
        <Fragment>
            <PanelResizeHandle className="h-1 bg-gray hover:bg-gray-300 hover:cursor-col-resize  transition-colors" />
            <div className='h-10 bg-muted/50 border-t-2 flex justify-between items-center'>
                <Tabs value={activeTab} onValueChange={setActiveTab} className="text-sm">
                    <TabsList>
                        <TabsTrigger value="lineage">
                            <Network className="h-4 w-4 mr-2" />
                            Lineage
                        </TabsTrigger>
                        <TabsTrigger value="results">
                            <Table className="h-4 w-4 mr-2" />
                            Preview
                        </TabsTrigger>
                    </TabsList>
                </Tabs>
                <div className="mr-2">
                    {
                        activeTab === "results" && (
                            <Button size='sm'
                                onClick={runQueryPreview}
                                disabled={isQueryLoading}
                                variant="outline"
                            >
                                {isQueryLoading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Play className="h-4 w-4 mr-2" />}
                                Preview Query
                            </Button>
                        )
                    }
                    {
                        activeTab === "lineage" && (
                            <Button size='sm'
                                onClick={() => fetchFileBasedLineage(activeFile?.node.path || "")}
                                disabled={lineageData[activeFile?.node.path || ""]?.isLoading}
                                variant="outline"
                            >
                                {lineageData[activeFile?.node.path || ""]?.isLoading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <RefreshCcw className="h-4 w-4 mr-2" />}
                                Refresh
                            </Button>
                        )
                    }
                </div>
            </div >
            <Panel defaultSize={40} className='border-t flex items-center justify-center'>
                <div className="flex flex-col w-full h-full flex-grow-1">
                    {activeTab === "results" && (
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
                    )}
                    {activeTab === "lineage" && (
                        <div>
                            {/* <ErrorBoundary FallbackComponent={() => (
                                <div>Something went wrong</div>
                            )}> */}
                            <>
                                {lineageData && lineageData[activeFile?.node.path] && lineageData[activeFile?.node.path].isLoading ? (
                                    <div className='flex items-center justify-center text-gray-300'><Loader2 className='h-6 w-6 animate-spin' /></div>
                                ) : (
                                    lineageData && lineageData[activeFile?.node.path] && lineageData[activeFile?.node.path].data && (
                                        <LineageView key={activeFile?.node.path} lineage={lineageData[activeFile?.node.path].data.lineage} rootAsset={lineageData[activeFile?.node.path].data.root_asset} style={{ height: '600px' }} />
                                    )
                                )}
                            </>
                            {/* </ErrorBoundary> */}
                        </div>
                    )}
                </div>
            </Panel>
        </Fragment >
    )
}