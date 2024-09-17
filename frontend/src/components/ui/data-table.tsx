"use client"

import { useState, useMemo, useEffect } from "react"
import {
    ColumnDef,
    ColumnFiltersState,
    SortingState,
    VisibilityState,
    flexRender,
    getCoreRowModel,
    getFacetedRowModel,
    getFacetedUniqueValues,
    getFilteredRowModel,
    getPaginationRowModel,
    getSortedRowModel,
    useReactTable,
} from "@tanstack/react-table"

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"

import { DataTablePagination } from "@/components/ui/data-table-pagination"
import { DataTableToolbar } from "@/components/ui/data-table-toolbar"
import { useRouter } from "next/navigation"
import { useAppContext } from "@/contexts/AppContext"
import { columns } from "@/components/table-viewer/asset-viewer-columns"
import { useAssets } from "@/contexts/AssetViewerContext"
import { Loader2 } from "lucide-react"

export default function DataTable() {
    const [rowSelection, setRowSelection] = useState({})
    const [columnVisibility, setColumnVisibility] =
        useState<VisibilityState>({
            tags: false,
            unique_name: false,
        })
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>(
        []
    )
    const [pagination, setPagination] = useState({
        pageIndex: 0,
        pageSize: 50,
    })
    const router = useRouter()

    const { assets, isLoading, submitSearch, sorting, setSorting } = useAssets()


    console.log({ assets })

    useEffect(() => {
        submitSearch()
    }, [])


    const data = useMemo(() => {
        const resources = assets.resources
        if (!assets || !assets.results) return []

        return assets.results.map((asset: any) => {
            const resource = resources.find((r: any) => r.id === asset.resource_id)
            return {
                ...asset,
                resource_name: resource?.name,
                resource_subtype: resource?.subtype,
                resource_has_dbt: resource?.has_dbt,
            }
        })
    }, [assets])

    const table = useReactTable({
        data,
        columns,
        state: {
            sorting,
            columnVisibility,
            rowSelection,
            columnFilters,
            pagination,
        },
        enableRowSelection: true,
        onRowSelectionChange: setRowSelection,
        onSortingChange: setSorting,
        onColumnFiltersChange: setColumnFilters,
        onColumnVisibilityChange: setColumnVisibility,
        onPaginationChange: setPagination,
        getCoreRowModel: getCoreRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        manualPagination: true,
        pageCount: assets.total_pages || -1,
        rowCount: assets.count || 0,
        getFacetedRowModel: getFacetedRowModel(),
        getFacetedUniqueValues: getFacetedUniqueValues(),
    })

    return (
        <div className="space-y-4">
            <DataTableToolbar table={table} />
            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        {table.getHeaderGroups().map((headerGroup) => (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map((header) => {
                                    return (
                                        <TableHead key={header.id} colSpan={header.colSpan}>
                                            {header.isPlaceholder
                                                ? null
                                                : flexRender(
                                                    header.column.columnDef.header,
                                                    header.getContext()
                                                )}
                                        </TableHead>
                                    )
                                })}
                            </TableRow>
                        ))}
                    </TableHeader>
                    <TableBody>
                        {table.getRowModel().rows?.length ? (
                            table.getRowModel().rows.map((row) => (
                                <TableRow
                                    className={`cursor-pointer ${isLoading ? 'bg-gray-50 animate-pulse' : ''}`}
                                    key={row.id}
                                    data-state={row.getIsSelected() && "selected"}
                                    onClick={() => {
                                        if (row?.original?.id) {
                                            router.push(`/assets/${row.original.id}`)
                                        }
                                    }}
                                >
                                    {row.getVisibleCells().map((cell) => (
                                        <TableCell key={cell.id}>
                                            {flexRender(
                                                cell.column.columnDef.cell,
                                                cell.getContext()
                                            )}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            ))
                        ) : (
                            <>
                                {isLoading ? (
                                    Array.from({ length: 20 }).map((_, rowIndex) => (
                                        <TableRow key={rowIndex}>
                                            {Array.from({ length: columns.length }).map((_, index) => (
                                                <TableCell key={index} className="animate-pulse">
                                                    <div className="h-4 bg-gray-200 rounded"></div>
                                                </TableCell>
                                            ))}
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow>
                                        <TableCell
                                            colSpan={columns.length}
                                            className="h-24 text-center"
                                        >
                                            No results.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </>
                        )}
                    </TableBody>
                </Table>
            </div>
            <DataTablePagination table={table} />
        </div >
    )
}
