import { AgGridReact } from "ag-grid-react";
import { useTheme } from "next-themes";
import Papa from "papaparse";
import { useMemo } from "react";

type CsvPreviewProps = {
  content: string;
  gridRef: any;
};

export default function CsvPreview({ content, gridRef }: CsvPreviewProps) {
  const { resolvedTheme } = useTheme();
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
        resolvedTheme === "dark" ? "ag-theme-balham-dark" : "ag-theme-balham"
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
