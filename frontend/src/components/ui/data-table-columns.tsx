"use client"

import { ColumnDef } from "@tanstack/react-table"

import { Badge } from "@/components/ui/badge"

import { DataTableColumnHeader } from "@/components/ui/data-table-column-header"
import { Asset } from "./schema"
import { getResourceIcon } from "@/lib/utils"



export const columns: ColumnDef<Asset>[] = [
    // {
    //     id: "select",
    //     header: ({ table }) => (
    //         <Checkbox
    //             checked={
    //                 table.getIsAllPageRowsSelected() ||
    //                 (table.getIsSomePageRowsSelected() && "indeterminate")p
    //             }
    //             onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
    //             aria-label="Select all"
    //             className="translate-y-[2px]"
    //         />
    //     ),
    //     cell: ({ row }) => (
    //         <Checkbox
    //             checked={row.getIsSelected()}
    //             onCheckedChange={(value) => row.toggleSelected(!!value)}
    //             aria-label="Select row"
    //             className="translate-y-[2px]"
    //         />
    //     ),
    //     enableSorting: false,
    //     enableHiding: false,
    // },
    {
        id: "resource",
        accessorFn: (row) => ({
            resource_subtype: row.resource_subtype,
            resource_has_dbt: row.resource_has_dbt,
            resource_name: row.name,
            resource_id: row.id
        }),
        filterFn: (row, id, value) => {
            const rowValue = row.getValue(id) as { resource_id: string };
            return value.includes(rowValue.resource_id);
        },
        enableSorting: false,
        header: ({ column }) => (
            <DataTableColumnHeader column={column} title="Source" />
        ),
        cell: ({ row }) => {
            const { resource_subtype, resource_name, resource_has_dbt } = row.getValue("resource") as any

            return (
                <div className='flex space-x-2 items-center'>
                    <div className='space-y-1'>
                        <div>{getResourceIcon(resource_subtype)}</div>
                        <div>{resource_has_dbt && getResourceIcon('dbt')}</div>
                    </div>
                    <div>{resource_name}</div>
                </div>
            )
        },
    },
    {
        accessorKey: "name",
        header: ({ column }) => (
            <DataTableColumnHeader column={column} title="Name" />
        ),
        cell: ({ row }) => <div className="font-semibold">{row.getValue("name")}</div>,
        enableSorting: false,
        enableHiding: false,
    },
    {
        accessorKey: "type",
        enableSorting: false,
        filterFn: (row, id, value) => {
            return value.includes(row.getValue(id))
        },
        header: ({ column }) => (
            <DataTableColumnHeader column={column} title="Type" />
        ),
        cell: ({ row }) => {
            return (
                <div>
                    {row.getValue("type") ? <Badge variant="outline">{(row.getValue("type") as string).toUpperCase()}</Badge> : ''}
                </div>
            )
        },
    },
    {
        accessorKey: "description",
        header: ({ column }) => (
            <DataTableColumnHeader column={column} title="Description" />
        ),
        cell: ({ row }) => <div className="w-[300px]">{row.getValue("description")}</div>,
        enableSorting: false,
        enableHiding: true,
    },
    // {
    //     accessorKey: "num_columns",
    //     header: ({ column }) => (
    //         <DataTableColumnHeader column={column} title="Num Cols" />
    //     ),
    //     cell: ({ row }) => <div>{row.getValue("num_columns")}</div>,
    //     enableHiding: true,
    // },
    {
        accessorKey: "tags",
        header: ({ column }) => (
            <DataTableColumnHeader column={column} title="Tags" />
        ),
        cell: ({ row }) => {
            const tags = row.getValue("tags");
            return (
                <div>
                    {Array.isArray(tags) ? tags.map((tag: string) => (
                        <Badge key={tag} variant="secondary">{tag}</Badge>
                    )) : ''}
                </div>
            );
        },
        enableHiding: true,
        enableSorting: false,
    },

    // {
    //     accessorKey: "description",
    //     enableSorting: false,
    //     header: ({ column }) => (
    //         <DataTableColumnHeader column={column} title="Description" />
    //     ),
    //     cell: ({ row }) => {
    //         const status = statuses.find(
    //             (status) => status.value === row.getValue("status")
    //         )

    //         if (!status) {
    //             return null
    //         }

    //         return (
    //             <div className="flex w-[100px] items-center">
    //                 {status.icon && (
    //                     <status.icon className="mr-2 h-4 w-4 text-muted-foreground" />
    //                 )}
    //                 <span>{status.label}</span>
    //             </div>
    //         )
    //     },
    //     filterFn: (row, id, value) => {
    //         return value.includes(row.getValue(id))
    //     },
    // },
    // {
    //     accessorKey: "priority",
    //     header: ({ column }) => (
    //         <DataTableColumnHeader column={column} title="Priority" />
    //     ),
    //     cell: ({ row }) => {
    //         const priority = priorities.find(
    //             (priority) => priority.value === row.getValue("priority")
    //         )

    //         if (!priority) {
    //             return null
    //         }

    //         return (
    //             <div className="flex items-center">
    //                 {priority.icon && (
    //                     <priority.icon className="mr-2 h-4 w-4 text-muted-foreground" />
    //                 )}
    //                 <span>{priority.label}</span>
    //             </div>
    //         )
    //     },
    //     filterFn: (row, id, value) => {
    //         return value.includes(row.getValue(id))
    //     },
    // },
    // {
    //     id: "actions",
    //     cell: ({ row }) => <DataTableRowActions row={row} />,
    // },
]
