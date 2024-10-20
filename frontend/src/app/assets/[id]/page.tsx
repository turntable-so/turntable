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
import EmbeddedCard from "@/components/metabase/embedded-card"



function ColumnsTable({ columns }: {
    columns: {
        name: string
        type: string
        description: string
        tests: string[]
        is_unused: boolean
    }[]
}) {
    return (
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead className="w-[200px] text-wrap pl-4">Name</TableHead>
                    <TableHead className="w-[150px] text-wrap">Data Type</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Tests</TableHead>
                    <TableHead>Usage</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {columns.sort((a, b) => a.name.localeCompare(b.name)).map((column) => (
                    <TableRow key={column.name} className="text-gray-500">
                        <TableCell className="text-black font-medium pl-4">{column.name}</TableCell>
                        <TableCell>{column.type}</TableCell>
                        <TableCell className="pr-4">{column.description}</TableCell>
                        <TableCell>{column.tests?.map((test) => <Badge variant='secondary' key={test}>{test}</Badge>)}</TableCell>
                        <TableCell>{column.is_unused && <Badge variant='outline'>Unused</Badge>}</TableCell>
                    </TableRow>
                ))}
            </TableBody>
        </Table>
    )
}

const EMBEDDING_KEY = 'a1ed35e2bec9192530c1bd26c3b0248cae3c8acfb0ed54eeb30d816eedac1f42'

const init = {
    headers: {
        "Content-Type": "application/json",
        "X-API-KEY": 'mb_cs2je3H5w5rLjpPkqOIDWnW4fBP0tXPRR4vN/HAFQG4=',
    },
};

const host = "http://metabase:4000";

async function getGroups() {
    const response = await fetch(`${host}/api/permissions/group`, {
        ...init,
    });
    return response.json();
}

async function updateCard(id: string) {
    const response = await fetch(`${host}/api/card/${id}`, {
        method: 'PUT',
        headers: init.headers,
        body: JSON.stringify({
            enable_embedding: true,
        })
    });
    return response.json();
}

async function getCards(id: string) {
    const response = await fetch(`${host}/api/card/${id}`, init);
    return response.json();
}

async function makeEmbeddable(id: string) {
    const response = await fetch(`${host}/api/card/${id}`, {
        method: 'PUT',
        headers: init.headers,
        body: JSON.stringify({
            enable_embedding: true,
        })
    });
    return response.json();
}


export default async function AssetPage({ params }: { params: { id: string } }) {

    const asset = await getAssetPreview(params.id)

    // extract the number 2 from this kind of id:
    // "0:urn:li:dashboard:(metabase,2)"
    const decodedId = decodeURIComponent(params.id);
    const questionId = decodedId.split(',').pop()?.replace(')', '') || '';
    console.log({ questionId })

    // const groups = await getGroups()
    // console.log({ groups })

    // const token = await fetch('/api/metabase')
    // useEffect(() => {
    //     const fetchData = async () => {
    //         const result = await updateCard('12')
    //         const response = await fetch(
    //             'http://localhost:3000/api/metabase/iframe_url?questionId=17',
    //             {
    //                 method: 'GET'
    //             }
    //         )
    //         console.log({ response })
    //         const iframeUrl = await response.json()
    //         console.log('iframeUrl')
    //         console.log({ iframeUrl })

    //         console.log({ result })

    //     }
    //     fetchData()
    // }, [])




    // const metabaseCardId = decodeURIComponent(params.id).split(',').pop()?.replace(')', '') || '';
    // console.log({ metabaseCardId });

    // const cards = await getCards(metabaseCardId)
    // // very interesting stuff in here, we could pull our last_used at field as well as view count
    // console.log({ cards })

    // const result = await makeEmbeddable('17')
    // console.log({ result })




    return (
        <div className="w-full  flex justify-center">
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
                    <div>
                        <div className="font-medium text-muted-foreground my-1  text-lg">Preview</div>
                        <Card className="rounded-md">
                            <CardContent className="p-4">
                                <EmbeddedCard questionId={Number(questionId)} />
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
        </div>
    )
}
