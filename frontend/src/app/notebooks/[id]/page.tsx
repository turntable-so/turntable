'use client'
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Collaboration from '@tiptap/extension-collaboration'
import CollaborationCursor from '@tiptap/extension-collaboration-cursor'
import * as Y from 'yjs'
import { WebrtcProvider } from 'y-webrtc'
import { useEffect, useState } from "react"
import { Separator } from '@/components/ui/separator'
import { Plus } from 'lucide-react'

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

    const [ydoc] = useState(() => new Y.Doc())
    const [provider] = useState(() => new WebrtcProvider('notebook-room', ydoc))

    const editor = useEditor({
        extensions: [
            StarterKit.configure({
                // The Collaboration extension comes with its own history handling
                history: false,
            }),
            Collaboration.configure({
                document: ydoc,
            }),
            CollaborationCursor.configure({
                provider: provider,
            }),
        ],
        content: 'Hello, collaborative world!',
    })

    useEffect(() => {
        // Clean up the WebRTC connection when the component unmounts
        return () => provider.destroy()
    }, [provider])

    return <div className="flex flex-col overflow-y-scroll h-screen w-full items-center">
        <div className='max-w-5xl w-full'>
            <div className="p-12 w-full">
                {blocks.map((block, i) => (
                    i % 2 === 0 ? (
                        <div key={i}>
                            <textarea className="w-full min-h-24" key={block.id} value={block.content} onChange={(e) => setBlocks(blocks.map((b) => b.id === block.id ? { ...b, content: e.target.value } : b))} />
                        </div>
                    ) : (
                        <div key={i} className="flex items-center gap-2 hover:bg-accent/25 rounded-md cursor-pointer px-2 py-1" onClick={
                            () => setBlocks([
                                ...blocks.slice(0, i),
                                { id: crypto.randomUUID(), content: "" },
                                ...blocks.slice(i)
                            ])
                        }>
                            <Separator />
                            <Plus className='w-8 h-8 text-muted-foreground' />
                            <Separator />
                        </div>
                    )
                ))}
                <div className="w-full">
                    <div className="flex items-center gap-2 hover:bg-accent/25 rounded-md cursor-pointer px-2 py-1" onClick={
                        () => setBlocks([...blocks, { id: crypto.randomUUID(), content: "" }])
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