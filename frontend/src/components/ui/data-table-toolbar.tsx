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
                    size="lg"
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
    // Calculate unique sources, types, and tags directly
    const uniqueSources = (() => {
        const sources: Record<string, string> = {}
        table.getCoreRowModel().rows.forEach((row) => {
            const resource = row.getValue("resource") as { resource_name: string, resource_id: string } | undefined;
            if (resource) {
                sources[resource.resource_id] = resource.resource_name
            }
        });
        return Object.entries(sources).map(([value, label]) => ({
            label,
            value,
        }));
    })();

    const uniqueTypes = (() => {
        const types = new Set<string>();
        table.getCoreRowModel().rows.forEach((row) => {
            const type = row.getValue("type") as string | undefined;
            if (type) types.add(type);
        });
        return Array.from(types).map(type => ({
            label: type,
            value: type,
        }));
    })();

    const uniqueTags = (() => {
        const tags = new Set<string>();
        table.getCoreRowModel().rows.forEach((row) => {
            const rowTags = row.getValue("tags") as string[] | undefined;
            if (rowTags) rowTags.forEach(tag => tags.add(tag));
        });
        return Array.from(tags).map(tag => ({
            label: tag,
            value: tag,
        }));
    })();

    console.log({ uniqueSources, uniqueTypes, uniqueTags })

    return (
        <div className="flex items-center justify-between">
            <div className="flex flex-1 items-center space-x-2">
                <div className="space-y-4">
                    <Input
                        autoFocus
                        placeholder="Search assets"
                        value={(table.getColumn("name")?.getFilterValue() as string) ?? ""}
                        onChange={(event) =>
                            table.getColumn("name")?.setFilterValue(event.target.value)
                        }
                        className="h-10 w-[500px]"
                    />
                    <div className="flex space-x-2">
                        {table.getColumn("resource") && (
                            <DataTableFacetedFilter
                                column={table.getColumn("resource")}
                                title="Source"
                                options={uniqueSources}
                            />
                        )}
                        {table.getColumn("type") && (
                            <DataTableFacetedFilter
                                column={table.getColumn("type")}
                                title="Type"
                                options={uniqueTypes}
                            />
                        )}
                        {table.getColumn("tags") && (
                            <DataTableFacetedFilter
                                column={table.getColumn("tags")}
                                title="Tags"
                                options={uniqueTags}
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
                </div>
            </div>
            <DataTableViewOptions table={table} />
        </div>
    )
}
