'use client'
import { useEffect, useState } from "react"
import { Separator } from '@/components/ui/separator'
import { DatabaseZap, FileText, MessageSquare, Plus } from 'lucide-react'
import { Textarea } from "@/components/ui/textarea"
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"
import { Button } from "@/components/ui/button"
import QueryBlock from "@/components/QueryBlock"
import { useAppContext } from "@/contexts/AppContext"
// Define the Block type
type Block = {
    id: string;
    content: string;
}

export default function NotebookPage() {
    const [blocks, setBlocks] = useState<Block[]>([
        {
            id: crypto.randomUUID(),
            content: "Hello, world!"
        }
    ])

    const { runQuery } = useAppContext();


    return <div className="flex flex-col overflow-y-scroll h-screen w-full items-center">
        <div className='max-w-7xl w-full'>
            <div className="p-12 w-full space-y-8">
                {blocks.map((block, i) => (
                    <div key={i}>
                        <Textarea
                            className="border-gray-100 shadow-none w-full min-h-24 resize-none overflow-hidden"
                            key={block.id}
                            value={block.content}
                            onChange={(e) => {
                                e.target.style.height = 'auto';
                                e.target.style.height = e.target.scrollHeight + 'px';
                                setBlocks(blocks.map((b) => b.id === block.id ? { ...b, content: e.target.value } : b));
                            }}
                            style={{ height: 'auto', overflow: 'hidden' }}
                        />
                    </div>

                ))}
                <div className="w-full">
                    <div className="flex items-center gap-2  rounded-md px-2 py-1">
                        <Separator />
                        <div>
                            <div className="flex space-x-2 p-2">
                                <Button variant="outline" size="sm" className="flex items-center hover:opacity-80 opacity-40">
                                    <DatabaseZap className="mr-2 h-4 w-4" />
                                    Query
                                </Button>
                                <Button variant="outline" size="sm" className="flex items-center hover:opacity-80 opacity-40" onClick={() => {
                                    setBlocks([...blocks, { id: crypto.randomUUID(), content: "" }])
                                }}>
                                    <FileText className="mr-2 h-4 w-4" />
                                    Text
                                </Button>
                                <Button variant="outline" size="sm" className="flex items-center hover:opacity-80 opacity-40" >
                                    <MessageSquare className="mr-2 h-4 w-4" />
                                    Prompt
                                </Button>
                            </div>
                        </div>
                        <Separator />
                    </div>
                </div>
                <QueryBlock
                    onRunQueryClick={() => runQuery('key')}
                    database={'database'}
                    title={'title'} key={'key'} onSqlChange={(sql: string) => undefined} />
            </div>
        </div>
    </div>
}