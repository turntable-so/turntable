import { ChartComponent } from "@/components/QueryBlock";
import MultiSelect from "@/components/ui/multi-select";
import { AgGridReact } from "ag-grid-react";
import { useEffect, useRef, useState } from "react";


import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAppContext } from "@/contexts/AppContext";

export default function ChartComposer({
  data,
}: {
  data: {
    colDefs: any[];
    rowData: any[];
  };
}) {
  const gridRef = useRef<AgGridReact>(null);

  const { notebookCharts, setNotebookCharts, activeNode } = useAppContext();

  const [currentOptions, setCurrentOptions] = useState(
    notebookCharts[activeNode]
  );

  useEffect(() => {
    setCurrentOptions(notebookCharts[activeNode]);
  }, [notebookCharts, activeNode]);

  useEffect(() => {
    if (currentOptions?.xAxis && currentOptions?.isXAxisNumeric) {
      const minXAxisValue = Math.min(
        ...data.rowData.map((row) => row[currentOptions?.xAxis])
      );
      setNotebookCharts({
        ...notebookCharts,
        [activeNode]: {
          ...notebookCharts[activeNode],
          xAxisRange: [minXAxisValue, minXAxisValue + 30],
        },
      });
    }
  }, [
    data.rowData,
    currentOptions?.xAxis,
    currentOptions?.isXAxisNumeric,
    activeNode,
  ]);

  useEffect(() => {
    if (currentOptions?.xAxis) {
      setNotebookCharts({
        ...notebookCharts,
        [activeNode]: {
          ...notebookCharts[activeNode],
          isXAxisNumeric: data.rowData.every(
            (row) => typeof row[currentOptions?.xAxis] === "number"
          ),
        },
      });
    }
  }, [data, currentOptions?.xAxis]);

  const handleRangeChange = (event: any) => {
    const { name, value } = event.target;
    setNotebookCharts({
      ...notebookCharts,
      [activeNode]: {
        ...notebookCharts[activeNode],
        xAxisRange:
          name === "min"
            ? [value, currentOptions?.xAxisRange[1]]
            : [currentOptions?.xAxisRange[0], value],
      },
    });
  };

  const chartColors = ["#2563eb", "#60a5fa"];
  return (
    <div>
      <div className="flex w-full h-full justify-between">
        <div className="flex-grow-1 w-4/5  flex-col items-between">
          <div className="flex flex-col w-full h-2/3 flex-grow-1">
            <ChartComponent
              chartType={currentOptions?.chartType}
              xAxis={currentOptions?.xAxis}
              yAxisSeriesList={currentOptions?.yAxisSeriesList}
              data={data.rowData}
              isXAxisNumeric={currentOptions?.isXAxisNumeric}
              xAxisRange={currentOptions?.xAxisRange}
            />
          </div>

          <div className="flex flex-col w-full h-full mb-8">
            <AgGridReact
              className="ag-theme-custom"
              ref={gridRef}
              suppressRowHoverHighlight={true}
              columnHoverHighlight={true}
              rowData={data.rowData}
              pagination={true}
              // @ts-ignore
              columnDefs={data.colDefs}
            />
          </div>
        </div>
        <div className="w-1/5 p-2 space-y-4">
          <div className="">
            <div className="text-lg py-2">Type</div>
            <Select
              defaultValue={currentOptions?.chartType || "BAR"}
              onValueChange={(val) => {
                setNotebookCharts({
                  ...notebookCharts,
                  [activeNode]: {
                    ...notebookCharts[activeNode],
                    chartType: val,
                  },
                });
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select an X Axis column" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="HBAR">Horizontal Bar Chart</SelectItem>
                <SelectItem value="BAR">Bar Chart</SelectItem>
                <SelectItem value="LINE">Line Chart</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <div className="text-lg py-2 font-semibold">X Axis</div>
            <div>
              <div>X Axis Column</div>
              <Select
                defaultValue={currentOptions?.xAxis as string}
                onValueChange={(val) => {
                  setNotebookCharts({
                    ...notebookCharts,
                    [activeNode]: {
                      ...notebookCharts[activeNode],
                      xAxis: val,
                    },
                  });
                }}
                value={currentOptions?.xAxis}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select an X Axis column" />
                </SelectTrigger>
                <SelectContent>
                  {data.colDefs.map((colDef) => (
                    <SelectItem key={colDef.field} value={colDef.field}>
                      {colDef.headerName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div>
            <div className="text-lg py-2 font-semibold">Y Axis</div>
            <MultiSelect
              items={currentOptions?.columnOptions.map((item: string) => ({
                label: item,
                value: item,
              }))}
              selected={currentOptions?.yAxisSeriesList}
              setSelected={() => { }}
              functionSelected={(newValue: any) => {
                setNotebookCharts({
                  ...notebookCharts,
                  [activeNode]: {
                    ...notebookCharts[activeNode],
                    yAxisSeriesList: newValue,
                  },
                });
              }}
              label="Select Y Axis columns"
            />
          </div>
          {currentOptions?.isXAxisNumeric && (
            <div>
              <div className="text-lg py-2 font-semibold">X Axis Range</div>
              <div className="flex space-x-2">
                <input
                  type="number"
                  name="min"
                  value={currentOptions?.xAxisRange[0]}
                  onChange={handleRangeChange}
                  className="w-1/2 p-2 border rounded"
                  placeholder="Min"
                />
                <input
                  type="number"
                  name="max"
                  value={currentOptions?.xAxisRange[1]}
                  onChange={handleRangeChange}
                  className="w-1/2 p-2 border rounded"
                  placeholder="Max"
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
