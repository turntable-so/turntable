import { useMemo } from "react";
import { AgGridReact } from "ag-grid-react";
import Papa from "papaparse";
import { useTheme } from "next-themes";

type CsvPreviewProps = {
  content: string;
  gridRef: any;
};

export default function CsvPreview({ content, gridRef }: CsvPreviewProps) {
  const { theme } = useTheme();
  const { rowData, columnDefs } = useMemo(() => {
    const parsedData = Papa.parse(content, { header: true });
    const { data, meta } = parsedData;

    const columns = meta.fields?.map((field: string) => ({
      headerName: field,
      field: field,
      editable: false,
    }));

    return {
      rowData: data,
      columnDefs: columns,
    };
  }, [content]);

  return (
    <AgGridReact
      className={
        theme === "dark" ? "ag-theme-material-dark" : "ag-theme-material"
      }
      ref={gridRef}
      suppressRowHoverHighlight={true}
      columnHoverHighlight={true}
      pagination={true}
      rowData={rowData}
      columnDefs={columnDefs}
    />
  );
}
