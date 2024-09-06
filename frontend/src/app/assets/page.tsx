'use client'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { AssetMap, useAppContext } from "@/contexts/AppContext"
import { Separator } from "@/components/ui/separator"
import { Box, DatabaseZap, Search, Tag } from 'lucide-react'
import { useRouter } from 'next/navigation'
import MultiSelect from "@/components/ui/multi-select"
import { Fragment, ReactNode, useCallback, useEffect, useState } from "react"

import MultiSelectCompact from "@/components/ui/multi-select-compact"
import { getResourceIcon } from "@/lib/utils"
import { DataTable } from "@/components/ui/data-table"
import { Asset } from "@/components/ui/schema"
import { columns } from "@/components/ui/data-table-columns"

// Import the tasks data
import tasksData from './tasks.json'




type Option = {
    value: string, label: string, icon?: ReactNode
}


export default function AssetsPage() {
    const {
        assets,
        resources
    } = useAppContext()
    const router = useRouter()

    const [filteredConnections, setFilteredConnections] = useState<string[]>([])
    const [filteredTypes, setFilteredTypes] = useState<string[]>([])
    const [filteredTags, setFilteredTags] = useState<string[]>([])
    const [query, setQuery] = useState<string>("")




    const allAssets = Object.entries(assets).reduce((acc, [resource_id, resource]) => {
        return acc.concat(
            resource.assets.map((asset: Asset) => ({
                ...asset,
                resource_id,
                resource_subtype: resources.find((r) => r.id === resource_id)?.subtype,
                resource_has_dbt: resources.find((r) => r.id === resource_id)?.has_dbt,
                resource_name: resources.find((r) => r.id === resource_id)?.name
            }))
        );
    }, []);


    let filteredAssets = allAssets.sort((a: Asset, b: Asset) => {
        return a.name.localeCompare(b.name)
    }).filter((asset: Asset) => {
        const matchesQuery = asset.name.toLowerCase().includes(query.toLowerCase());

        const filtersEnabled = filteredConnections.length > 0 || filteredTypes.length > 0 || filteredTags.length > 0;
        if (filtersEnabled) {
            const matchesConnectionFilter = filteredConnections.length > 0 ? filteredConnections.some(conn => conn === asset.resource_id) : true
            const matchesTypeFilter = filteredTypes.length > 0 ? filteredTypes.some(type => type === asset.type) : true
            const matchesTagsFilter = filteredTags.length > 0 ? (asset.tags?.length > 0 && filteredTags.some(tag => asset.tags.includes(tag))) : true

            return matchesConnectionFilter && matchesTypeFilter && matchesTagsFilter && matchesQuery
        }

        return matchesQuery
    });



    const allTypeOptions = Array.from(
        new Set([...allAssets.map((asset: Asset) => asset.type)])
    ).map((type: string) => ({
        value: type,
        label: type
    })).filter((option: Option) => option.value.length > 0)


    const allTagOptions = allAssets.reduce((acc: string[], asset: Asset) => {
        if (asset.tags && Array.isArray(asset.tags)) {
            asset.tags.forEach((tag: string) => {
                if (!acc.includes(tag)) {
                    acc.push(tag);
                }
            });
        }
        return acc;
    }, []).map((tag: string) => ({
        value: tag,
        label: tag
    })).filter((option: Option) => option.value.length > 0)

    const allConnectionOptions = Object.entries(assets).map(([resource_id, resource]) => ({
        value: resource_id,
        label: resource.name
    })).filter((option: Option) => option.value.length > 0)

    console.log({ allAssets })

    return (
        <div className='max-w-7xl w-full px-8 py-4 mt-4 mb-8'>
            <DataTable data={allAssets} columns={columns} />
        </div>
    )
}
