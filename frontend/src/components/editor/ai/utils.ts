export const generatePreviewForAI = (rowData: any, colDefs: any) => {
  const columns = colDefs.map((col: any) => col.field);
  const headers = colDefs.map((col: any) => col.headerName);
  const topRows = rowData.slice(0, 5);

  let table = `| ${headers.join(" | ")} |\n`;
  table += `| ${headers.map(() => "---").join(" | ")} |\n`;
  topRows.forEach((row: any) => {
    table += `| ${columns.map((field: any) => String(row[field])).join(" | ")} |\n`;
  });

  return table;
};
