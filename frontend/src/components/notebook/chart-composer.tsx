import { useRef, useState, useEffect } from "react";
import { Button } from "../ui/button";
import { Bar, BarChart, CartesianGrid, XAxis } from "recharts"
import { ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { ChartConfig, ChartContainer } from "@/components/ui/chart"
import { AgGridReact } from "ag-grid-react";
import { FancyMultiSelect } from "@/components/ui/multi-select"


const chartData = [
    { month: "January", desktop: 186, mobile: 80 },
    { month: "February", desktop: 305, mobile: 200 },
    { month: "March", desktop: 237, mobile: 120 },
    { month: "April", desktop: 73, mobile: 190 },
    { month: "May", desktop: 209, mobile: 130 },
    { month: "June", desktop: 214, mobile: 140 },
]

const chartConfig = {
    desktop: {
        label: "Desktop",
        color: "#2563eb",
    },
    mobile: {
        label: "Mobile",
        color: "#60a5fa",
    },
} satisfies ChartConfig

import * as React from "react"

import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectLabel,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"


export default function ChartComposer({ data }: {
    data: {
        colDefs: any[]
        rowData: any[]
    }
}) {

    const gridRef = useRef<AgGridReact>(null);

    type Direction = 'ASCENDING' | 'DESCENDING'
    type ChartType = 'BAR'

    const [chartType, setChartType] = useState<ChartType>('BAR')
    const [xAxis, setXAxis] = useState<string | null>(null)
    const [yAxisSeriesList, setYAxisSeriesList] = useState<string[]>([])
    const [sortIndex, setSortIndex] = useState<string | null>(null)
    const [sortDirection, setSortDirection] = useState<Direction>('ASCENDING')


    useEffect(() => {
        if (data.colDefs) {
            setXAxis(data.colDefs[0].field)
            setYAxisSeriesList(
                [...data.colDefs.slice(1).map((colDef) => colDef.field)]
            )
        }
    }, [data.colDefs])

    return (
        <div>
            <div className='flex w-full h-full justify-between'>
                <div className='flex-grow-1 w-4/5  flex-col items-between'>
                    <div className='flex flex-col w-full h-2/3 flex-grow-1'>
                        <ChartContainer config={chartConfig} className="min-h-[400px] w-full">
                            <BarChart accessibilityLayer data={data.rowData}>
                                <CartesianGrid vertical={false} />
                                <XAxis
                                    dataKey={xAxis as string}
                                    tickLine={false}
                                    tickMargin={5}
                                    axisLine={false}
                                />
                                <ChartTooltip content={<ChartTooltipContent />} />
                                <Bar dataKey="num" fill="var(--color-desktop)" radius={4} />
                            </BarChart>
                        </ChartContainer>
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
                <div className='w-1/5 p-2 space-y-4'>
                    <div className=''>
                        <div className='text-lg py-2'>Type</div>
                        {/* @ts-ignore */}
                        <Select defaultValue={chartType} onValueChange={(val) => setChartType(val)}>
                            <SelectTrigger>
                                <SelectValue placeholder="Select an X Axis column" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="BAR">Bar Chart</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                    <div>
                        <div className='text-lg py-2 font-semibold'>X Axis</div>
                        <div>
                            <div>X Axis Column</div>
                            <Select defaultValue={xAxis as string} onValueChange={(val) => setXAxis(val)}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select an X Axis column" />
                                </SelectTrigger>
                                <SelectContent>
                                    {data.colDefs.map((colDef) => (
                                        <SelectItem key={colDef.field} value={colDef.field}>{colDef.headerName}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                    <div>
                        <div className='text-lg py-2 font-semibold'>Y Axis</div>
                        <FancyMultiSelect
                            items={yAxisSeriesList.map((item: string) => ({
                                label: item,
                                value: item,
                            }))}
                            selected={yAxisSeriesList as any}
                            setSelected={() => undefined}
                            label="Select Y Axis columns"
                        />
                    </div>
                    <div>
                        <div>
                            <div className='text-lg py-2 font-semibold'>Sort</div>
                        </div>
                        <div>
                            <div className='text-md text-muted-foreground py-2'>Sort Index</div>
                            <Select defaultValue={chartType} onValueChange={(val) => setChartType(val as any)}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select a chart type" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="BAR">Bar</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div>
                            <div className='text-md text-muted-foreground py-2'>Sort Direction</div>
                            <Select>
                                <SelectTrigger className="">
                                    <SelectValue placeholder="Select a chart type" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="bar">Bar</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    )
}