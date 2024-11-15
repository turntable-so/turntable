import { AgGridReact } from "ag-grid-react";
import SkeletonLoadingTable from "./skeleton-loading-table";
import { useFiles } from "@/app/contexts/FilesContext";
import CsvPreview from "./csv-preview";
import { useTheme } from "next-themes";
import ErrorMessage from "../error-message";

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
  const { theme } = useTheme();
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
          <ErrorMessage error={queryPreviewError} />
        </div>
      );
    case isCsvPreviewable:
      return <CsvPreview content={activeFileContent} gridRef={gridRef} />;
    default:
      return (
        <AgGridReact
          className={
            theme === "dark" ? "ag-theme-balham-dark" : "ag-theme-balham"
          }
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
