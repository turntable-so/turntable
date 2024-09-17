import { getAssetPreview } from "@/app/actions/actions"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { getLineage } from '@/app/actions/actions'
import { LineageView } from '@/components/lineage/LineageView'



import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import ExploreInLineageViewerButton from "@/components/assets/explore-in-lineage-viewer-button"
import { getResourceIcon } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import LineagePreview from "@/components/lineage/LineagePreview"


function ColumnsTable({ columns }: {
    columns: {
        name: string
        type: string
        description: string
    }[]
}) {
    return (
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead className="w-[200px] text-wrap pl-4">Name</TableHead>
                    <TableHead className="w-[150px] text-wrap">Data Type</TableHead>
                    <TableHead>Description</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {columns.map((column) => (
                    <TableRow key={column.name} className="text-gray-500">
                        <TableCell className="text-black font-medium pl-4">{column.name}</TableCell>
                        <TableCell>{column.type}</TableCell>
                        <TableCell className="pr-4">{column.description}</TableCell>
                    </TableRow>
                ))}
            </TableBody>
        </Table>
    )
}

export default async function AssetPage({ params }: { params: { id: string } }) {

    const asset = await getAssetPreview(params.id)

    return (
        <div className="max-w-7xl w-full px-16 pt-16">
            <div className="flex gap-4 items-center">
                <div className="mb-8">
                    <h1 className="text-2xl font-medium text-black">{asset.name}</h1>
                    <div className="flex gap-6 my-2 items-center">
                        <div>
                            <div className="flex gap-2 items-center">
                                <div>{getResourceIcon(asset.resource_subtype)}</div>
                                <div>{asset.resource_has_dbt && getResourceIcon('dbt')}</div>
                                <div className='text-sm text-gray-500'>{asset.unique_name}</div>
                            </div>
                        </div>
                        <Badge variant='outline'>{asset.type.toUpperCase()}</Badge>
                    </div>
                </div>
            </div>
            <div className="flex flex-col gap-8 w-full pb-12">
                <div>
                    <div className="font-medium text-muted-foreground my-1 text-lg">Details</div>
                    <Card className="rounded-md">
                        <CardContent className="p-4">
                            <div className="flex gap-6">
                                <div>
                                    <p className="text-sm text-gray-500">Schema</p>
                                    <p className="text-sm my-1">{asset.schema}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-gray-500">Dataset</p>
                                    <p className="text-sm my-1">{asset.dataset}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-gray-500">Table</p>
                                    <p className="text-sm my-1">{asset.table_name}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-gray-500">Tags</p>
                                    <div className="flex gap-2 my-1">
                                        {asset.tags ? <p className="text-sm text-gray-500">{
                                            asset.tags.map((tag: string) => <Badge variant="secondary" key={tag}>{tag}</Badge>)
                                        }</p> : <p className="text-sm text-gray-500 italic">No tags</p>}
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
                <div>
                    <div className="font-medium text-muted-foreground my-1  text-lg">Summary</div>
                    <Card className="rounded-md">
                        <CardContent className="p-4">
                            <div>
                                {asset.description ? <p className="text-sm">{asset.description}</p> : <p className="text-sm italic">No description</p>}
                            </div>
                        </CardContent>
                    </Card>
                </div>
                {asset.columns && (
                    <div>
                        <div className="font-medium text-muted-foreground my-1  text-lg">Columns</div>
                        <Card className="rounded-md">
                            <ColumnsTable columns={asset.columns} />
                        </Card>
                    </div>
                )}
                <div>
                    <div className="flex justify-between items-center">
                        <div className="font-medium text-muted-foreground my-1 text-lg">Lineage</div>
                        <ExploreInLineageViewerButton asset={asset} />
                    </div>
                    <Card className="rounded-md h-[600px] ">
                        <LineagePreview nodeId={params.id} />
                    </Card>
                </div>
            </div>
        </div>
    )
}
