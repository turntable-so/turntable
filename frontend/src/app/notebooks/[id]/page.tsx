'use client'
import { useEditor } from '../../../packages/headless/src/components/novel'
import { ScrollArea } from "../../../components/ui/scroll-area"
import { extensions as defaultExtensions } from '../../../components/notebook/extensions'
import QueryBlock from '../../../components/QueryBlock'
import { getNotebook, updateNotebook } from '../../actions/actions'
import { HotkeysProvider } from 'react-hotkeys-hook'

import { defaultEditorContent } from "../../../lib/content";
import {
    EditorCommand,
    EditorCommandEmpty,
    EditorCommandItem,
    EditorCommandList,
    EditorContent,
    type EditorInstance,
    EditorRoot,
    type JSONContent,
} from "novel";
import { ImageResizer, StarterKit, handleCommandNavigation } from "novel/extensions";
import { Fragment, SyntheticEvent, useEffect, useRef, useState } from "react";
import { useDebouncedCallback } from "use-debounce";
import { ColorSelector } from "../../../components/notebook/selectors/color-selector";
import { LinkSelector } from "../../../components/notebook/selectors/link-selector";
import { NodeSelector } from "../../../components/notebook/selectors/node-selector";
import { Separator } from "../../../components/ui/separator";

import { handleImageDrop, handleImagePaste } from "novel/plugins";
import GenerativeMenuSwitch from "../../../components/notebook/generative/generative-menu-switch";
import { TextButtons } from "../../../components/notebook/selectors/text-buttons";
import { slashCommand, suggestionItems } from "../../../components/notebook/slash-command";
import { Button } from '../../../components/ui/button'
import { useCurrentEditor } from '@tiptap/react'
import { useAppContext } from '../../../contexts/AppContext'
import { Badge } from '@/components/ui/badge'
import { Loader2 } from 'lucide-react'
import { useParams, useRouter } from 'next/navigation';
import { Input } from '@/components/ui/input'
import { set } from 'date-fns'
import * as Dialog from '@radix-ui/react-dialog';
import { AgGridReact } from 'ag-grid-react'

import FullScreenDialog from '@/components/FullScreenDialog'
import ChartComposer from '@/components/notebook/chart-composer'


const InsertContentEventListener = () => {
    const { editor } = useEditor();

    const { insertCurrentSqlContent } = useAppContext()

    useEffect(() => {
        const appendToDocument = ({
            sql, title,
            resourceId,
        }: { title: string, sql: string, resourceId: string }) => {
            editor?.chain().focus('end')
                .createParagraphNear()
                .setSqlNode({
                    title,
                    sql,
                    resourceId: resourceId,
                    limit: 1000,
                })
                .createParagraphNear()
                .insertContent({
                    type: 'text',
                    text: '\n'
                })
                .createParagraphNear()
                .insertContent({
                    type: 'text',
                    text: '\n'
                })
                .run();
        };

        if (insertCurrentSqlContent) {
            appendToDocument(insertCurrentSqlContent)
        }
    }, [insertCurrentSqlContent])



    return null
}



const hljs = require('highlight.js');

const extensions = [...defaultExtensions, slashCommand];

const AdvancedEditor = ({ setSaveStatus }: {
    setSaveStatus: (status: "Saving" | "Saved" | "Error") => void;
}) => {
    const [initialContent, setInitialContent] = useState<null | JSONContent>(null);
    const params = useParams()
    const notebookId = params.id as string



    const [charsCount, setCharsCount] = useState();

    const [openNode, setOpenNode] = useState(false);
    const [openColor, setOpenColor] = useState(false);
    const [openLink, setOpenLink] = useState(false);
    const [openAI, setOpenAI] = useState(false);


    const debouncedUpdates = useDebouncedCallback(async (editor: EditorInstance) => {
        const json = editor.getJSON();
        await updateNotebook(notebookId, { json_contents: JSON.stringify(json) });
        setSaveStatus("Saved");
    }, 500);

    useEffect(() => {
        const fetchNotebook = async (id: string) => {
            const notebook = await getNotebook(id as string)
            console.log({ contents: notebook.contents })
            setInitialContent(JSON.parse(notebook.contents))
        }
        if (notebookId) {
            fetchNotebook(notebookId as string)
        }
    }, [notebookId]);

    if (!initialContent) return null;

    return (
        <div className='w-full'>
            <EditorRoot>
                <EditorContent
                    initialContent={initialContent}
                    extensions={extensions}
                    editorProps={{
                        handleDOMEvents: {
                            keydown: (_view, event) => handleCommandNavigation(event),
                        },
                        // handlePaste: (view, event) => handleImagePaste(view, event, uploadFn),
                        // handleDrop: (view, event, _slice, moved) => handleImageDrop(view, event, moved, uploadFn),
                        attributes: {

                            class:
                                "prose prose-lg dark:prose-invert prose-headings:font-title font-default focus:outline-none max-w-full",
                        },
                    }}
                    onUpdate={({ editor }) => {
                        debouncedUpdates(editor);
                        setSaveStatus("Saving");
                    }}
                    slotAfter={<ImageResizer />}
                >
                    <InsertContentEventListener />

                    <EditorCommand className="z-50 h-auto max-h-[330px] overflow-y-auto rounded-md border border-muted bg-white px-1 py-2 shadow-md transition-all">
                        <EditorCommandEmpty className="px-2 text-muted-foreground">No results</EditorCommandEmpty>
                        <EditorCommandList>
                            {suggestionItems.map((item: any) => (
                                <EditorCommandItem
                                    value={item.title}
                                    onCommand={(val) => item.command(val)}
                                    className="flex w-full items-center space-x-2 rounded-md px-2 py-1 text-left text-sm hover:bg-accent aria-selected:bg-accent"
                                    key={item.title}
                                >
                                    <div className="flex h-10 w-10 items-center justify-center rounded-md border border-muted bg-background">
                                        {item.icon}
                                    </div>
                                    <div>
                                        <p className="font-medium">{item.title}</p>
                                        <p className="text-xs text-muted-foreground">{item.description}</p>
                                    </div>
                                </EditorCommandItem>
                            ))}
                        </EditorCommandList>
                    </EditorCommand>

                    <GenerativeMenuSwitch open={openAI} onOpenChange={setOpenAI}>
                        <Separator orientation="vertical" />
                        <NodeSelector open={openNode} onOpenChange={setOpenNode} />
                        <Separator orientation="vertical" />

                        <LinkSelector open={openLink} onOpenChange={setOpenLink} />
                        <Separator orientation="vertical" />
                        <TextButtons />
                        <Separator orientation="vertical" />
                        <ColorSelector open={openColor} onOpenChange={setOpenColor} />
                    </GenerativeMenuSwitch>
                </EditorContent>
            </EditorRoot>
        </div>
    );
};




export default function Page() {
    type SaveStatus = "Saving" | "Saved" | "Error";
    const [saveStatus, setSaveStatus] = useState<SaveStatus>("Saved");

    const [title, setTitle] = useState<string>('')
    const [isDialogOpen, setIsDialogOpen] = useState(true);
    const gridRef = useRef<AgGridReact>(null);


    const params = useParams()
    const { isFullScreen, fullScreenData, setFullScreenData, setIsFullScreen } = useAppContext()
    const notebookId = params.id as string

    useEffect(() => {
        const fetchNotebook = async (id: string) => {
            const notebook = await getNotebook(id as string)
            setTitle(notebook.title)
        }
        if (notebookId) {
            fetchNotebook(notebookId as string)
        }
    }, [notebookId])

    const updateTitle = useDebouncedCallback(async (title: string) => {
        await updateNotebook(notebookId, { title });
        setSaveStatus("Saved");
    }, 500);

    const handleTitleChange = (e: any) => {
        setTitle(e.target.value)
        setSaveStatus("Saving")
        updateTitle(e.target.value)

    }

    const closeFullScreen = () => {
        setIsFullScreen(false)
        setFullScreenData(null)
    }

    return (
        <Fragment>
            <ScrollArea className='flex flex-col h-full items-center'>
                <div className='flex flex-col h-full items-center'>
                    <div className="px-20 py-12 w-full">
                        <div className='flex h-8 justify-end'>
                            <Badge className='opacity-65' variant='secondary'>
                                {saveStatus === "Saving" && (
                                    <Loader2 className="bg-zinc-200 h-3 w-3 animate-spin opacity-50 mr-1" />
                                )}
                                <div>
                                    {saveStatus}
                                </div>
                            </Badge>

                        </div>
                        <div className='my-8 flex flex-wrap'>
                            <input className="w-full border-none focus:outline-none scroll-m-20 text-4xl font-bold tracking-tight text-gray-800" value={title} onChange={handleTitleChange} />
                        </div>
                        <AdvancedEditor setSaveStatus={setSaveStatus} />
                        <div className='h-6' />
                    </div>
                </div>
            </ScrollArea>
            {isFullScreen && (
                <FullScreenDialog isOpen={isFullScreen} onOpenChange={setIsDialogOpen}>
                    <Button variant='ghost' onClick={closeFullScreen}>X</Button>
                    <ChartComposer data={fullScreenData} />
                </FullScreenDialog>
            )}
        </Fragment>
    );
}