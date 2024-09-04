import { ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";

import { ChartConfig, ChartContainer } from "@/components/ui/chart";
import {
    BarChart,
    CartesianGrid,
    XAxis,
    YAxis,
    Bar,
    LineChart,
    Line,
} from "recharts";
import { useState, useEffect } from "react";


const chartConfig = {
    desktop: {
        label: "Desktop",
        color: "#2563eb",
    },
    mobile: {
        label: "Mobile",
        color: "#60a5fa",
    },
} satisfies ChartConfig;
const chartColors = ["#2563eb", "#60a5fa"];

export default function Chart(props: any) {
    const {
        chartType,
        xAxis,
        yAxisSeriesList,
        data,
        isXAxisNumeric,
        xAxisRange,
    } = props;
    const [filteredData, setFilteredData] = useState<any>([]);
    console.log({
        data,
        xAxis,
        yAxisSeriesList,
        isXAxisNumeric,
        xAxisRange,
        filteredData,
        chartType,
    })

    const setData = () => {
        if (isXAxisNumeric && data) {
            const filteredData = data.filter(
                (row) => row[xAxis] >= xAxisRange[0] && row[xAxis] <= xAxisRange[1]
            ); getColumnType
            setFilteredData(filteredData);
        } else {
            setFilteredData(filteredData);
        }
    };

    useEffect(() => {
        setData();
    }, [xAxisRange, xAxis, data, isXAxisNumeric]);


    return (
        <ChartContainer config={chartConfig} className="min-h-[400px] w-full">
            {chartType === "BAR" ? (
                <BarChart accessibilityLayer data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        dataKey={xAxis as string}
                        tickLine={false}
                        tickMargin={5}
                        axisLine={false}
                    />
                    <YAxis />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    {(yAxisSeriesList || []).map((series: any, index: any) => (
                        <Bar
                            isAnimationActive={false}
                            key={'tax_rate'}
                            dataKey={'tax_rate'}
                            fill={chartColors[index % 2]}
                        />
                    ))}
                </BarChart>
            ) : chartType === "HBAR" ? (
                <BarChart accessibilityLayer data={data} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        dataKey={xAxis as string}
                        tickLine={false}
                        tickMargin={5}
                        axisLine={false}
                    />
                    <YAxis type="number" />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    {(yAxisSeriesList || []).map((series: any, index: any) => (
                        <Bar
                            isAnimationActive={false}
                            key={'tax_rate'}
                            dataKey={'tax_rate'}
                            fill={chartColors[index % 2]}
                        />
                    ))}
                </BarChart>
            ) : (
                <LineChart accessibilityLayer data={filteredData}>
                    <CartesianGrid vertical={false} />
                    <XAxis
                        dataKey={xAxis as string}
                        tickLine={false}
                        tickMargin={5}
                        axisLine={false}
                    />
                    <YAxis />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    {(yAxisSeriesList || []).map((series: any, index: any) => (
                        <Line
                            isAnimationActive={false}
                            key={series.value}
                            dataKey={series.value}
                            fill={chartColors[index % 2]}
                        />
                    ))}
                </LineChart>
            )}
        </ChartContainer>
    );
}
