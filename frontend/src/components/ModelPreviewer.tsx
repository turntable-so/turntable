'use client'
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "./ui/accordion";
import { Button } from './ui/button'
import { Scroll, SquareArrowOutUpRight, X } from "lucide-react";
import { ScrollArea } from "./ui/scroll-area";
import { ColumnTypeIcon } from "./ColumnTypeIcon";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator"
import { Fragment, useEffect } from "react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./ui/tooltip";
import { useAppContext } from "../contexts/AppContext";


export default function ModelPreviewer({ asset, context, clearAsset }: { context?: 'NOTEBOOK' | 'LINEAGE', asset: any, clearAsset: () => void }) {

    const { setInsertCurrentSqlContent } = useAppContext();



    const insertAssetSqlIntoCurrentContext = () => {
        const sql = `SELECT\n  *\nFROM\n  ${asset.name}\nLIMIT 1000`;
        setInsertCurrentSqlContent({ sql, title: asset.name, resourceId: asset.resource_id });
    }

    return (
        <div className='w-full flex flex-col h-full'>
            <div className='flex justify-between items-center text-center bg-muted border-y'>
                {context === 'NOTEBOOK' && (
                    <div className='flex justify-between w-full'>
                        <Button onClick={() => clearAsset()} className='gap-1 flex items-center' size='sm' variant='ghost'>
                            <X className='w-4 h-4' />
                        </Button>
                        <Button onClick={insertAssetSqlIntoCurrentContext} className='gap-1 flex items-center' size='sm' variant='ghost'>
                            <div>Open in Notebook</div>
                            <SquareArrowOutUpRight className='w-4 h-4' />
                        </Button>
                    </div>
                )}
            </div>
            <div className='flex flex-col h-full mt-4'>
                <ScrollArea className=''>
                    <div className='border-none space-y-4 text-sm text-wrap'>
                        <div >
                            <div className='border-none px-4 no-underline hover:no-underline bg-muted py-2 font-semibold text-sm'>
                                Model Details
                            </div>
                            <div className='border-none p-4 space-y-4'>
                                <div>
                                    <div>
                                        Model Name
                                    </div>
                                    <div className='font-medium text-gray-700'>{asset.name}</div>
                                </div>
                                <div>
                                    <div>
                                        Dataset
                                    </div>
                                    <div className='font-medium text-gray-700'>{asset.dataset}</div>
                                </div>
                                <div>
                                    <div>
                                        Schema
                                    </div>
                                    <div className='font-medium text-gray-700'>{asset.schema}</div>
                                </div>
                                <div>
                                    <div>
                                        Table
                                    </div>
                                    <div className='font-medium text-gray-700'>{asset.table_name}</div>
                                </div>
                                <div>
                                    <div>
                                        Description
                                    </div>
                                    {asset.description ? (
                                        <div className='font-medium'>{asset.description}</div>

                                    ) : (
                                        <div className='italic text-muted-foreground opacity-60'>No description</div>
                                    )}
                                </div>
                                <div>
                                    <div className='font-bold'>
                                        URL
                                    </div>
                                    {asset.config?.url ? (
                                        <a href={asset.config?.url} target="_blank" className="text-blue-500 lowercase">
                                            {asset.config?.url}
                                        </a>

                                    ) : (
                                        <div className='italic text-muted-foreground opacity-60'>No url</div>
                                    )}
                                </div>
                                {asset.tags && (

                                    <div>
                                        <div>
                                            Tags
                                        </div>
                                        <div className='font-normal grid space-y-2 mt-1 ml-[-8px]'>
                                            {asset.tags.map((test: string, i: number) => (
                                                <Badge variant='secondary' className='w-fit text-muted-foreground' key={i}>{test}</Badge>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                <div>
                                    <div>
                                        Materialization
                                    </div>
                                    <div className='font-mono font-medium'>{asset.materialization}</div>
                                </div>
                                <div>
                                    <div>
                                        Tests
                                    </div>
                                    {asset.tests ? (
                                        <div className='font-normal grid space-y-2 mt-1 ml-[-8px]'>
                                            {asset.tests.map((test: string, i: number) => (
                                                <Badge variant='secondary' className='w-fit text-muted-foreground' key={i}>{test}</Badge>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className='italic text-muted-foreground opacity-60'>No tests</div>
                                    )}

                                </div>
                            </div>
                        </div>
                        {asset.columns && (
                            <div>
                                <div className='border-none px-4 no-underline hover:no-underline bg-muted py-2 font-semibold text-sm'>
                                    {`Columns(${asset.columns.length})`}
                                </div>
                                <div className='space-y-2'>
                                    {asset.columns.map((column: any, i: number) => (
                                        <Fragment key={i}>
                                            <div className='p-4'>
                                                <div className=''>
                                                    <div className='font-bold font-mono'>{column.name}</div>
                                                    <div className='font-mono font-medium text-gray-400 flex items-center text-xs'><ColumnTypeIcon dataType={column.type} className="size-4 mr-1" />{column.type}</div>
                                                    <div className='font-normal grid gric- space-y-2 ml-[-8px]'>
                                                        {(column.tests || []).map((test: string, i: number) => (
                                                            <Badge variant='secondary' className='w-fit text-muted-foreground' key={i}>{test}</Badge>
                                                        ))}
                                                    </div>
                                                    <div className='pt-1 font-normal'>{column.description}</div>
                                                </div>
                                            </div>
                                            <Separator className='text-black' />

                                        </Fragment>

                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                    <div className="h-24" />
                </ScrollArea>
            </div>
        </div >
    )
}