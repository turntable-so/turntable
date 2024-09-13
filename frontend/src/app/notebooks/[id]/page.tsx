'use client'
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Plus } from "lucide-react"
import { useState } from "react"


export default function NotebookPage() {

    const [blocks, setBlocks] = useState<Block[]>([
        {
            id: 1,
            content: "Hello, world!"
        }
    ])
    return <div className="flex flex-col overflow-y-scroll h-screen w-full">
        <div className='max-w-5xl mx-auto'>
            <div className="p-12 w-full">
                {blocks.map((block) => (
                    <textarea className="w-full min-h-24" key={block.id} value={block.content} onChange={(e) => setBlocks(blocks.map((b) => b.id === block.id ? { ...b, content: e.target.value } : b))} />
                ))}
                <div className="w-full">
                    <div className="flex items-center gap-2 hover:bg-accent/25 rounded-md cursor-pointer px-2 py-1" onClick={
                        () => setBlocks([...blocks, { id: blocks.length + 1, content: "" }])
                    }>
                        <Separator />
                        <Plus className='w-8 h-8 text-muted-foreground' />
                        <Separator />
                    </div>
                </div>
            </div>
        </div>
    </div>
}