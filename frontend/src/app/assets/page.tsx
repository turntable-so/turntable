'use client'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { AssetMap, useAppContext } from "@/contexts/AppContext"
import { Separator } from "@/components/ui/separator"
import { Box, DatabaseZap, Search, Tag } from 'lucide-react'
import { useRouter } from 'next/navigation'
import MultiSelect from "@/components/ui/multi-select"
import { Fragment, ReactNode, useCallback, useState } from "react"

import MultiSelectCompact from "@/components/ui/multi-select-compact"
import { getResourceIcon } from "@/lib/utils"


type Asset = {
    id: string;
    name: string;
    type: string;
    unique_name: string;
    resource_id: string;
    description: string;
    num_columns: number;
    tags: string[];
};


type Option = {
    value: string, label: string, icon?: ReactNode
}


export default function AssetsPage() {
    const {
        assets,
        resources
    } = useAppContext()
    const router = useRouter()

    console.log({ resources })

    const [filteredConnections, setFilteredConnections] = useState<string[]>([])
    const [filteredTypes, setFilteredTypes] = useState<string[]>([])
    const [filteredTags, setFilteredTags] = useState<string[]>([])
    const [query, setQuery] = useState<string>("")
    const [currentPage, setCurrentPage] = useState(1)
    const totalPages = 97

    const allAssets = Object.entries(assets).reduce((acc, [resource_id, resource]) => {
        return acc.concat(
            resource.assets.map((asset: Asset) => ({
                ...asset,
                resource_id
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





    return (
        <div className='max-w-7xl w-full px-8 py-4'>
            <div className='px-8 py-8 flex flex-col items-center'>
                <div className='w-full'>
                    <div className="flex items-center border border-gray-200 rounded-md focus-within:border-black mb-4">
                        <Search className="h-4 w-4 text-gray-500 ml-3" />
                        <Input
                            type="search"
                            placeholder="Search for models, datasets, charts & more..."
                            className="p-6 text-black font-medium border-0 focus-visible:ring-0 focus-visible:ring-offset-0"
                            onChange={(e) => { setQuery(e.target.value) }}
                            autoFocus
                        />

                    </div>
                    <div className='flex gap-4 flex items-center justify-between'>
                        <div className='text-sm font-medium text-gray-500 pl-1'>Showing {filteredAssets.length} of {allAssets.length} assets</div>
                        <div className='flex gap-2'>
                            <div className='w-[200px]'>
                                <MultiSelectCompact
                                    renderIcon={() => <DatabaseZap className="h-4 w-4 text-muted-foreground" />}
                                    label="Connection"
                                    options={allConnectionOptions}
                                    onValueChange={setFilteredConnections}
                                    defaultValue={filteredConnections}
                                    placeholder="Connections"
                                    animation={2}
                                    maxCount={1}
                                />
                            </div>
                            <div className='w-[160px]'>
                                <MultiSelectCompact
                                    renderIcon={() => <Box className="h-4 w-4 text-muted-foreground" />}
                                    label="Type"
                                    options={allTypeOptions}
                                    onValueChange={setFilteredTypes}
                                    defaultValue={filteredTypes}
                                    placeholder="Types"
                                    animation={2}
                                    maxCount={1}
                                />
                            </div>
                            <div className='w-[160px]'>
                                <MultiSelectCompact
                                    renderIcon={() => <Tag className="h-4 w-4 text-muted-foreground" />}
                                    label="Tag"
                                    options={allTagOptions}
                                    onValueChange={setFilteredTags}
                                    defaultValue={filteredTags}
                                    placeholder="Tags"
                                    animation={2}
                                    maxCount={1}
                                />
                            </div>
                        </div>
                    </div>
                </div>
                <div className='h-6' />
                {filteredAssets.length === 0 && <div className='w-full  flex justify-center h-48 items-center'>No assets found</div>}
                <div className='grid grid-cols-1 md:grid-cols-2 gap-6 w-full mt-4'>
                    {filteredAssets.map((asset: Asset) => (
                        <Card
                            key={asset.id}
                            className='hover:border-black hover:cursor-pointer rounded-md'
                            onClick={() => router.push(`/assets/${asset.id}`)}
                        >
                            <CardHeader>
                                <div className='flex items-center space-x-2'>
                                    <CardTitle>{asset.name.slice(0, 50)}</CardTitle>
                                </div>
                            </CardHeader>
                            <CardContent className="flex flex-col h-[125px] overflow-y-auto">
                                {asset.description?.trim().length > 0 ? (
                                    <p className="text-sm text-gray-500">
                                        {asset.description.length > 240
                                            ? `${asset.description.slice(0, 240)}...`
                                            : asset.description}
                                    </p>
                                ) : (
                                    <p className="text-sm text-gray-500">No description</p>
                                )}
                            </CardContent>
                            <CardFooter>
                                <div className='w-full flex justify-between items-center'>
                                    <div className='flex space-x-1'>
                                        <div>{getResourceIcon(resources.find(resource => resource.id === asset.resource_id).subtype)}</div>
                                        <div>{resources.find(resource => resource.id === asset.resource_id).has_dbt && getResourceIcon('dbt')}</div>
                                        <div className='text-sm text-gray-400'>{resources.find(resource => resource.id === asset.resource_id).name}</div>
                                    </div>
                                    <div className="flex justify-end gap-4">
                                        <div className="text-sm text-gray-400">{asset.type.toUpperCase()}</div>
                                        <div className="text-sm text-gray-400">{asset.num_columns} columns</div>
                                    </div>
                                </div>
                            </CardFooter>
                        </Card>
                    ))}
                </div>
            </div>
            <div className="h-6" />
        </div>
    )
}
