'use client'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { useAppContext } from "@/contexts/AppContext"
import { Separator } from "@/components/ui/separator"
import { Columns3, Search } from 'lucide-react'
import { useRouter } from 'next/navigation'
import MultiSelect from "@/components/ui/multi-select"
import { DatabaseZap2 } from 'lucide-react'
import { useState } from "react"


type Asset = {
    id: string;
    name: string;
    type: string;
    unique_name: string;
    resource_id: string;
    description: string;
    num_columns: number;
};


const frameworksList = [
    { value: "react", label: "React", icon: DatabaseZap2 },
    { value: "angular", label: "Angular", icon: DatabaseZap2 },
    { value: "vue", label: "Vue", icon: DatabaseZap2 },
    { value: "svelte", label: "Svelte", icon: DatabaseZap2 },
    { value: "ember", label: "Ember", icon: DatabaseZap2 },
];



export default function AssetsPage() {
    const {
        assets
    } = useAppContext()
    const router = useRouter()

    console.log({ assets })

    const [selectedFrameworks, setSelectedFrameworks] = useState([])
    const [query, setQuery] = useState("")


    const allAssets = Object.entries(assets).reduce((acc, [resource_id, resource]) => {
        return acc.concat(
            resource.assets.map((asset: Asset) => ({
                ...asset,
                resource_id
            }))
        );
    }, []);

    const filteredAssets = allAssets.filter((asset: Asset) => {
        return asset.name.toLowerCase().includes(query.toLowerCase())
    })


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
                        <div className='text-sm font-medium text-gray-500 pl-1'>Showing 1-200 of {allAssets.length} assets</div>
                        <div className='flex gap-2'>
                            <div>
                                <MultiSelect
                                    options={frameworksList}
                                    onValueChange={setSelectedFrameworks}
                                    defaultValue={selectedFrameworks}
                                    placeholder="Connections"
                                    animation={2}
                                    maxCount={1}
                                />
                            </div>
                            <div>
                                <MultiSelect
                                    options={frameworksList}
                                    onValueChange={setSelectedFrameworks}
                                    defaultValue={selectedFrameworks}
                                    placeholder="Types"
                                    animation={2}
                                    maxCount={1}
                                />
                            </div>
                            <div>
                                <MultiSelect
                                    options={frameworksList}
                                    onValueChange={setSelectedFrameworks}
                                    defaultValue={selectedFrameworks}
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
                            <CardContent className="flex h-24">
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
        </div>
    )
}
