"use client"

import { Cross2Icon } from "@radix-ui/react-icons"
import { Table } from "@tanstack/react-table"

import { Input } from "@/components/ui/input"


import * as React from "react"
import { CheckIcon, PlusCircledIcon } from "@radix-ui/react-icons"
import { Column } from "@tanstack/react-table"

import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
    CommandSeparator,
} from "@/components/ui/command"
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"
import { Separator } from "@/components/ui/separator"

import { DropdownMenuTrigger } from "@radix-ui/react-dropdown-menu"
import { MixerHorizontalIcon } from "@radix-ui/react-icons"

import {
    DropdownMenu,
    DropdownMenuCheckboxItem,
    DropdownMenuContent,
    DropdownMenuLabel,
    DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu"
import { DataTableFacetedFilter } from "./DataTableFacetedFilter"
import { useState } from "react"
import { useAssets } from "@/contexts/AssetViewerContext"
import { AsteriskSquare } from "lucide-react"

interface DataTableViewOptionsProps<TData> {
    table: Table<TData>
}


export function DataTableViewOptions<TData>({
    table,
}: DataTableViewOptionsProps<TData>) {
    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button
                    variant="outline"
                    size="sm"
                    className="ml-auto hidden h-8 lg:flex"
                >
                    <MixerHorizontalIcon className="mr-2 h-4 w-4" />
                    Display
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[150px]">
                <DropdownMenuLabel>Toggle columns</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {table
                    .getAllColumns()
                    .filter(
                        (column) =>
                            typeof column.accessorFn !== "undefined" && column.getCanHide()
                    )
                    .map((column) => {
                        return (
                            <DropdownMenuCheckboxItem
                                key={column.id}
                                className="capitalize"
                                checked={column.getIsVisible()}
                                onCheckedChange={(value) => column.toggleVisibility(!!value)}
                            >
                                {column.id}
                            </DropdownMenuCheckboxItem>
                        )
                    })}
            </DropdownMenuContent>
        </DropdownMenu>
    )
}



interface DataTableToolbarProps<TData> {
    table: Table<TData>
}

export function DataTableToolbar<TData>({
    table,

}: DataTableToolbarProps<TData>) {
    const isFiltered = table.getState().columnFilters.length > 0
    const { query, setQuery, assets, fetchAssets, filters, setFilters } = useAssets();
    console.log({ assets })

    const onSubmit = () => {
        fetchAssets();
    };

    const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter') {
            onSubmit();
        }
    };



    return (
        <div>
            <div className="w-full">
                <div>
                    <div className="space-y-4 w-full">
                        <Input
                            autoFocus
                            placeholder="Search assets"
                            value={query}
                            onChange={(event) =>
                                setQuery(event.target.value)
                            }
                            onKeyDown={handleKeyDown}
                            className="h-10 w-full"
                        />
                        <div className="flex items-center justify-between">
                            <div className="flex space-x-2 items-center">
                                <div>
                                    <div className="ml-1 text-sm text-muted-foreground w-24">
                                        {assets?.count} results
                                    </div>
                                </div>
                                {table.getColumn("resource") && assets?.filters?.sources && (
                                    <DataTableFacetedFilter
                                        title="Source"
                                        selectedValues={filters.sources}
                                        setSelectedValues={(sources) => setFilters({
                                            ...filters,
                                            sources
                                        })}
                                        options={assets.filters.sources.map((resource: any) => (
                                            {
                                                label: assets.resources.find((r: any) => r.id === resource.resource__id)?.name,
                                                value: resource.resource__id,
                                                count: resource.count
                                            }
                                        ))}
                                    />
                                )}
                                {table.getColumn("type") && assets?.filters?.types && (
                                    <DataTableFacetedFilter
                                        selectedValues={filters.types}
                                        setSelectedValues={(types) => setFilters({
                                            ...filters,
                                            types,
                                        })}
                                        title="Type"
                                        options={assets.filters.types.map((type: any) => (
                                            {
                                                label: type.type,
                                                value: type.type,
                                                count: type.count
                                            }
                                        ))}
                                    />
                                )}
                                {table.getColumn("tags") && assets?.filters?.tags && (
                                    <DataTableFacetedFilter
                                        selectedValues={filters.tags}
                                        setSelectedValues={(tags) => setFilters({
                                            ...filters,
                                            tags,
                                        })}
                                        title="Tags"
                                        options={assets.filters.tags.map((tag: any) => (
                                            {
                                                label: tag.tags,
                                                value: tag.tags,
                                                count: tag.count
                                            }
                                        ))}
                                    />
                                )}
                                {isFiltered && (
                                    <Button
                                        variant="ghost"
                                        onClick={() => table.resetColumnFilters()}
                                        className="h-8 px-2 lg:px-3"
                                    >
                                        Reset
                                        <Cross2Icon className="ml-2 h-4 w-4" />
                                    </Button>
                                )}
                            </div>
                            <div>
                                <DataTableViewOptions table={table} />
                            </div>
                        </div>
                    </div>
                </div>

            </div>

        </div>
    )
}
