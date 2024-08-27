'use client'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { AssetMap, useAppContext } from "@/contexts/AppContext"
import { Separator } from "@/components/ui/separator"
import { Search } from 'lucide-react'
import { useRouter } from 'next/navigation'
import MultiSelect from "@/components/ui/multi-select"
import { Fragment, ReactNode, useCallback, useState } from "react"

import MultiSelectCompact from "@/components/ui/multi-select-compact"


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
        assets
    } = useAppContext()
    const router = useRouter()

    console.log({ assets })

    const [filteredConnections, setFilteredConnections] = useState<Option[]>([])
    const [filteredTypes, setFilteredTypes] = useState<Option[]>([])
    const [filteredTags, setFilteredTags] = useState<Option[]>([])
    const [query, setQuery] = useState("")
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


    let filteredAssets = allAssets.filter((asset: Asset) => {
        console.log({ asset, filteredTypes })
        const matchesQuery = asset.name.toLowerCase().includes(query.toLowerCase());
        const filtersEnabled = filteredConnections.length > 0 || filteredTypes.length > 0 || filteredTags.length > 0;

        const matchesConnection = filteredConnections.some(conn => conn.value === asset.resource_id);
        const matchesType = filteredTypes.some(type => type.value === asset.type);
        console.log({ matchesType })
        const matchesTags = (asset.tags?.length > 0 ? filteredTags.some(tag => asset.tags.includes(tag.value)) : false);

        console.log(filteredTypes.some(type => type.value === asset.type))

        return matchesQuery && filtersEnabled ? (matchesConnection || matchesType || matchesTags) : true
    });



    const allTypeOptions = Array.from(
        new Set([...allAssets.map((asset: Asset) => asset.type)])
    ).map((type: string) => ({
        value: type,
        label: type
    }))


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
    }))

    const allConnectionOptions = Object.entries(assets).map(([resource_id, resource]) => ({
        value: resource_id,
        label: resource.name
    }))

    const handlePageChange = useCallback((newPage: number) => {
        // This function would typically fetch new data or update the view
        setCurrentPage(newPage)
        console.log(`Navigating to page ${newPage}`)
    }, [])

    const getPageNumbers = () => {
        const pageNumbers = [1, 2, 3]
        if (currentPage > 3 && currentPage < totalPages - 1) {
            pageNumbers.push(currentPage)
        }
        if (totalPages > 4) {
            pageNumbers.push(totalPages)
        }
        return pageNumbers
    }


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
                                    label="Connections"
                                    options={allConnectionOptions}
                                    onValueChange={setFilteredConnections}
                                    defaultValue={filteredConnections}
                                    placeholder="Connections"
                                    animation={2}
                                    maxCount={1}
                                />
                            </div>
                            <div className='w-[150px]'>
                                <MultiSelectCompact
                                    label="Types"
                                    options={allTypeOptions}
                                    onValueChange={setFilteredTypes}
                                    defaultValue={filteredTypes}
                                    placeholder="Types"
                                    animation={2}
                                    maxCount={1}
                                />
                            </div>
                            <div className='w-[150px]'>
                                <MultiSelectCompact
                                    label="Tags"
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
                <div className='grid grid-cols-1 md:grid-cols-2 gap-6 w-full mt-4'>
                    {filteredAssets.map((asset: Asset) => (
                        <Card
                            key={asset.id}
                            className='hover:border-black hover:cursor-pointer rounded-md'
                            onClick={() => router.push(`/assets/${asset.id}`)}
                        >
                            <CardHeader>
                                <CardTitle>{asset.name.slice(0, 50)}</CardTitle>
                            </CardHeader>
                            <CardContent className="flex">
                                {asset.description?.trim().length > 0 ? <p className="text-sm text-gray-500">{asset.description.slice(0, 240)}</p> : <p className="text-sm text-gray-500">No description</p>}
                            </CardContent>
                            <CardFooter>
                                <div className="w-full flex justify-end gap-4">
                                    <div className="text-sm text-gray-400">{asset.type.toUpperCase()}</div>
                                    <div className="text-sm text-gray-400">{asset.num_columns} columns</div>
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
