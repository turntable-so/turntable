import { AgGridReact } from "ag-grid-react";
import SkeletonLoadingTable from "./skeleton-loading-table";
import { useFiles } from "@/app/contexts/FilesContext";
import CsvPreview from "./csv-preview";

interface PreviewPanelProps {
  isQueryLoading: boolean;
  queryPreviewError: string | null;
  bottomPanelHeight?: number;
  gridRef: any;
  rowData: any;
  colDefs: any;
}

export default function PreviewPanel({
  isQueryLoading,
  queryPreviewError,
  bottomPanelHeight,
  gridRef,
  rowData,
  colDefs,
}: PreviewPanelProps) {
  const { activeFile } = useFiles();

  const activeFileContent = activeFile?.content;
  const isCsvPreviewable =
    activeFileContent &&
    typeof activeFileContent === "string" &&
    activeFile.node.name.endsWith(".csv") &&
    activeFile.node.type === "file";

  switch (true) {
    case isQueryLoading:
      return <SkeletonLoadingTable />;
    case !!queryPreviewError:
      return (
        <div
          style={{
            height: bottomPanelHeight,
          }}
          className="overflow-y-scroll p-6"
        >
          <div className="text-red-500 text-sm">{queryPreviewError}</div>
          <div className="h-24" />
        </div>
      );
    case isCsvPreviewable:
      return <CsvPreview content={activeFileContent} gridRef={gridRef} />;
    default:
      return (
        <AgGridReact
          className="ag-theme-custom"
          ref={gridRef}
          suppressRowHoverHighlight={true}
          columnHoverHighlight={true}
          pagination={true}
          rowData={rowData}
          columnDefs={colDefs}
        />
      );
  }
}
