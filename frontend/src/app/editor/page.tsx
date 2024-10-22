'use client'
import { Tree, TreeApi } from 'react-arborist'
import { useState, useEffect, Fragment, useCallback, useRef } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { executeQueryPreview, getBranches, infer } from '../actions/actions'
import useResizeObserver from "use-resize-observer";
import { Box, Check, ChevronDown, ChevronRight, CircleArrowUp, Ellipsis, File, FileText, Folder, FolderOpen, GitBranch, Loader2, PanelBottom, PanelLeft, PanelRight, Pencil, Play, Plus, Trash, X } from 'lucide-react'
import Editor, { DiffEditor } from '@monaco-editor/react';
import { FilesProvider, useFiles, FileNode, OpenedFile } from '../contexts/FilesContext';
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { AgGridReact } from 'ag-grid-react'
import "@/components/ag-grid-custom-theme.css"; // Custom CSS Theme for Data Grid
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Command, CommandEmpty, CommandGroup, CommandItem, CommandList } from '@/components/ui/command'
import { Textarea } from '@/components/ui/textarea'
import FileSearchCommand from '@/components/editor/FileSearchCommand'
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area'
import React from 'react'
import BottomPanel from '@/components/editor/bottom-panel'
import { LineageProvider } from '../contexts/LineageContext'
import EditorSidebar from '@/components/editor/editor-sidebar'

const PromptBox = ({ setPromptBoxOpen }: { setPromptBoxOpen: (open: boolean) => void }) => {

    const { activeFile, setActiveFile, updateFileContent } = useFiles();

    const [prompt, setPrompt] = useState('')
    const [model, setModel] = useState<'PROMPT' | 'CONFIRM'>('PROMPT')
    const [isLoading, setIsLoading] = useState(false)

    const callInference = async () => {
        if (activeFile) {
            setIsLoading(true)
            const response = await infer({
                filepath: activeFile.node.path,
                content: activeFile.content,
                instructions: prompt,
            })
            if (response.content) {
                setActiveFile({
                    ...activeFile,
                    view: 'diff',
                    diff: {
                        original: activeFile.content,
                        modified: response.content
                    }
                })
                setModel('CONFIRM')
            }
            setIsLoading(false)
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
            e.preventDefault();
            callInference();
        }
    }

    const handleEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
            setPromptBoxOpen(false);
        }
    };

    useEffect(() => {
        document.addEventListener('keydown', handleEscape);
        return () => {
            document.removeEventListener('keydown', handleEscape);
        };
    }, []);

    useEffect(() => {
        const textarea = document.querySelector('textarea');
        if (textarea) {
            textarea.addEventListener('keydown', handleKeyDown as any);
            return () => {
                textarea.removeEventListener('keydown', handleKeyDown as any);
            };
        }
    }, []);

    return (
        <div className='border-b py-2 mb-2'>
            <div className="flex flex-col items-center w-full px-4">
                <Textarea className='w-full my-2 z-100' autoFocus placeholder="Add materialization to this model" value={prompt} onChange={(e) => setPrompt(e.target.value)} disabled={isLoading} />
                <div className='flex space-x-2 justify-end w-full'>
                    <>
                        {model === 'PROMPT' ? (
                            <>
                                <Button
                                    size='sm'

                                    variant='outline'
                                    className='rounded-sm'
                                    onClick={() => setPromptBoxOpen(false)}
                                >
                                    Cancel
                                </Button>
                                <Button
                                    size='sm'
                                    disabled={!prompt || isLoading}
                                    variant='default'
                                    className='rounded-sm'
                                    onClick={() => {
                                        callInference()
                                    }}
                                >
                                    {isLoading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : 'Generate'}
                                </Button>
                            </>
                        ) : (
                            <>
                                <Button
                                    size='sm'

                                    variant='destructive'
                                    className='rounded-sm'
                                    onClick={() => {
                                        if (activeFile) {
                                            setActiveFile({
                                                ...activeFile,
                                                view: 'edit',
                                            })
                                        }
                                        setPromptBoxOpen(false)
                                    }}
                                >
                                    <X className='mr-2 size-4' />
                                    Reject
                                </Button>
                                <Button
                                    size='sm'
                                    disabled={!prompt || isLoading}
                                    variant='default'
                                    className='rounded-sm'
                                    onClick={() => {
                                        updateFileContent(activeFile?.node.path || '', activeFile?.diff?.modified || '');
                                        setActiveFile({
                                            ...activeFile,
                                            isDirty: true,
                                            content: activeFile?.diff?.modified || '',
                                            view: 'edit',
                                            diff: undefined
                                        } as OpenedFile)
                                        setPromptBoxOpen(false)
                                    }}
                                >
                                    <Check className='mr-2 size-4' />
                                    Accept
                                </Button>
                            </>
                        )}
                    </>
                </div>
            </div>
        </div>
    )
}


function EditorContent({ setPromptBoxOpen, containerWidth }: { setPromptBoxOpen: (open: boolean) => void, containerWidth: number }) {
    const { activeFile, updateFileContent, saveFile, activeFilepath, setActiveFile } = useFiles();

    // Define your custom theme
    const customTheme = {
        base: 'vs',
        inherit: true,
        rules: [],
        colors: {
            'editor.foreground': '#000000',
            'editorLineNumber.foreground': '#A1A1AA',
        }
    };


    if (activeFile?.view === 'diff') {
        return (
            <DiffEditor
                text-muted-foreground original={activeFile?.diff?.original || ''}
                modified={activeFile?.diff?.modified || ''}
                width={containerWidth - 2}
                language='sql'
                options={{
                    minimap: { enabled: false },
                    scrollbar: {
                        vertical: 'visible',
                        horizontal: 'visible',
                        verticalScrollbarSize: 8,
                        horizontalScrollbarSize: 8,
                        verticalSliderSize: 8,
                        horizontalSliderSize: 8,
                    },
                    lineNumbers: 'on',
                    wordWrap: 'on',
                    fontSize: 14,
                    lineNumbersMinChars: 3,
                }}
                theme="mutedTheme"
            />
        );
    }

    if (activeFile?.view === 'new') {
        return (
            <div className='h-full w-full flex items-center justify-center'>
                <div className='w-full max-w-4xl'>
                    <Input placeholder='Ask AI, search for files & run commands' />
                </div>
                <div>
                    asd
                </div>
            </div>
        )
    }


    return (
        <Editor
            key={activeFile?.node.path}
            value={activeFile?.content || ''}
            onChange={(value) => {
                console.log('onchange', { value, activeFile })
                if (activeFile) {
                    updateFileContent(activeFile.node.path, value || '');
                    setActiveFile({
                        ...activeFile,
                        content: value || '',
                    })
                }
            }}
            language='sql'
            options={{
                minimap: { enabled: false },
                scrollbar: {
                    vertical: 'visible',
                    horizontal: 'visible',
                    verticalScrollbarSize: 8,
                    horizontalScrollbarSize: 8,
                    verticalSliderSize: 8,
                    horizontalSliderSize: 8
                },
                lineNumbers: 'on',
                wordWrap: 'on',
                fontSize: 14,
                lineNumbersMinChars: 3,
                renderLineHighlight: 'none',
            }}
            width={containerWidth - 2}
            beforeMount={(monaco) => {
                monaco.editor.defineTheme('mutedTheme', {
                    ...customTheme,
                    colors: {
                        ...customTheme.colors,
                        'editor.lineHighlightBackground': 'var(--muted)',
                        'editor.lineHighlightBorder': 'var(--muted)',
                    }
                } as any);
                monaco.editor.setTheme('mutedTheme');
            }}
            onMount={(editor, monaco) => {
                monaco.editor.setTheme('mutedTheme');

                // Add cmd+k as a monaco keyboard listener
                editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyK, () => {
                    console.log('Cmd+K pressed in Monaco editor');
                    setPromptBoxOpen(true)
                });

                // Prevent default behavior for cmd+s
                editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, (e: any) => {
                    console.log('Cmd+S pressed in Monaco editor');
                    saveFile(activeFile?.node.path || '', editor.getValue());
                });
            }}
            theme="mutedTheme"
        />
    );
}

type QueryPreview = {
    rows?: Object
    signed_url: string
}

function EditorPageContent() {
    const [leftWidth, setLeftWidth] = useState(20)
    const [rightWidth, setRightWidth] = useState(20)
    const [branches, setBranches] = useState([])
    const [activeBranch, setActiveBranch] = useState('')
    const { ref: treeContainerRef, width: treeWidth, height: treeHeight } = useResizeObserver();
    const { ref: topBarRef, width: topBarWidth, height: topBarHeight } = useResizeObserver();

    const { files, openedFiles, activeFile, openFile, setActiveFile, activeFilepath, closeFile, setActiveFilepath } = useFiles();

    const [showLeftSideBar, setShowLeftSidebar] = useState(true)
    const [showRightSideBar, setShowRightSidebar] = useState(false)
    const [showBottomPanel, setShowBottomPanel] = useState(true)

    const [promptBoxOpen, setPromptBoxOpen] = useState(false)
    const [colDefs, setColDefs] = useState([])
    const [rowData, setRowData] = useState([])
    const [isLoading, setIsLoading] = useState(false)
    const gridRef = useRef<AgGridReact>(null);
    const [queryPreview, setQueryPreview] = useState<QueryPreview | null>(null)

    const treeRef = useRef<any>(null);
    const [isSearchFocused, setIsSearchFocused] = useState(false);
    const searchInputRef = useRef<HTMLInputElement>(null);

    const [filesearchQuery, setFilesearchQuery] = useState('')
    const [selectedIndex, setSelectedIndex] = useState(0);
    const [queryPreviewError, setQueryPreviewError] = useState(null)

    useEffect(() => {
        if (treeRef.current) {
            const rootNode = treeRef.current.root;
            if (rootNode && rootNode.children.length > 0) {
                rootNode.children[0].open();
            }
        }
    }, [files]);

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.metaKey) {
                switch (event.key.toLowerCase()) {
                    case 'b':
                        event.preventDefault();
                        if (event.shiftKey) {
                            console.log('Cmd+Shift+B pressed');
                            setShowRightSidebar(!showRightSideBar)

                        } else {
                            console.log('Cmd+B pressed');
                            setShowLeftSidebar(!showLeftSideBar)
                        }
                        break;
                    case 'p':
                        event.preventDefault();
                        console.log('Cmd+P pressed');
                        searchInputRef.current?.focus();
                        break;
                    case 'j':
                        event.preventDefault();
                        console.log('Cmd+J pressed');
                        setShowBottomPanel(!showBottomPanel)
                        break;
                }
            }

            if (isSearchFocused) {
                switch (event.key) {
                    case 'ArrowUp':
                        event.preventDefault();
                        setSelectedIndex((prevIndex) => Math.max(0, prevIndex - 1));
                        break;
                    case 'ArrowDown':
                        event.preventDefault();
                        setSelectedIndex((prevIndex) => prevIndex + 1); // You might want to add a max limit based on search results
                        break;
                    case 'Enter':
                        event.preventDefault();
                        // Handle file selection here
                        console.log('File selected:', selectedIndex);
                        setIsSearchFocused(false);
                        setFilesearchQuery('');
                        break;
                }
            }
        };

        window.addEventListener('keydown', handleKeyDown);

        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, [showLeftSideBar, showRightSideBar, showBottomPanel, isSearchFocused, selectedIndex]);


    useEffect(() => {
        const fetchBranches = async () => {
            const { active_branch, branches } = await getBranches()
            setActiveBranch(active_branch)
            setBranches(branches)
        }
        fetchBranches()
    }, [])

    const runQueryPreview = async () => {
        setIsLoading(true)
        setQueryPreview(null)
        setQueryPreviewError(null)
        if (activeFile && activeFile.content) {
            const query = activeFile.content
            const preview = await executeQueryPreview(
                query,
            )
            if (preview.error) {
                setQueryPreviewError(preview.error)
            } else {
                setQueryPreview(preview)
            }
        }
        setIsLoading(false)
    }


    const getTablefromSignedUrl = async (signedUrl: string) => {
        const response = await fetch(signedUrl);
        if (response.ok) {
            const table = await response.json();
            console.log({ table })
            const defs = Object.keys(table.data[0]).map((key) => ({
                field: key,
                headerName: key,
                // type: [getColumnType(table.column_types[key])],
                // cellDataType: getColumnType(table.column_types[key]),
                editable: false,
                valueGetter: (p: any) => {
                    if (p.colDef.cellDataType === "date") {
                        return new Date(p.data[key]);
                    }
                    return p.data[key];
                },
                cellClass: "p-0",
            }));
            console.log({ defs, types: table.column_types });
            setColDefs(defs as any);
            setRowData(table.data);
            // setDefaultDataChart(table.data, defs);
        }
        setIsLoading(false);
    }

    console.log({ files })


    useEffect(() => {
        const fetchQueryPreview = async () => {
            if (queryPreview?.signed_url) {
                getTablefromSignedUrl(queryPreview.signed_url as string)
            }
        }
        fetchQueryPreview()
    }, [queryPreview?.signed_url])




    return (
        <div className='flex flex-col h-screen'>
            <PanelGroup direction="horizontal" className="h-fit">
                <Panel defaultSize={leftWidth} minSize={15} maxSize={30} onResize={setLeftWidth} className='border-r  text-gray-600'>
                    <EditorSidebar />
                </Panel>
                {/* <Panel defaultSize={leftWidth} minSize={15} maxSize={30} onResize={setLeftWidth} className='border-r bg-muted/50 text-gray-600'>
                    <Tabs defaultValue="files" className="h-full">
                        <div
                            className={cn(
                                "flex h-[52px] items-center justify-center",
                                "h-[52px]"
                            )}
                        >
                            <TabsList className="grid w-full grid-cols-2 mx-4">
                                <TabsTrigger value="files" className="flex items-center justify-center">
                                    <File className="w-4 h-4 mr-2" />
                                    Files
                                </TabsTrigger>
                                <TabsTrigger value="branch" className="flex items-center justify-center">
                                    <GitBranch className="w-4 h-4 mr-2" />
                                    Branch
                                </TabsTrigger>
                            </TabsList>
                        </div>
                        <Separator />
                        <TabsContent value="files" className='h-full px-2'>
                            <div className="h-full" ref={treeContainerRef}>
                                <Tree
                                    selection={activeFile?.node.path}
                                    height={treeHeight}
                                    width={treeWidth}
                                    data={files}
                                    openByDefault={false}
                                    indent={12}
                                    ref={treeRef}
                                    // @ts-ignore
                                    onCreate={onCreate}
                                    // @ts-ignore
                                    onRename={onRename}
                                    // @ts-ignore
                                    onMove={onMove}
                                    // @ts-ignore
                                    onDelete={onDelete}
                                >
                                    {Node as any}
                                </Tree>
                            </div>
                        </TabsContent>
                        <TabsContent value="branch">Branches</TabsContent>
                    </Tabs>
                </Panel> */}
                <PanelResizeHandle className="bg-transparent   transition-colors" />
                <Panel>
                    <div className="h-full bg-white" ref={topBarRef}>
                        <div className='hover:cursor-pointer flex items-center space-x-2 py-0 bg-muted'>
                            <div className='w-full' style={{
                                maxWidth: topBarWidth ? topBarWidth - 50 : '100%'
                            }}>
                                <ScrollArea className='w-full flex whitespace-nowrap overflow-x-scroll'>
                                    <div className='w-max flex overflow-x-scroll h-9'>
                                        {openedFiles.map((file: OpenedFile, index: number) => (
                                            <div
                                                key={file.node.path}
                                                onClick={() => {
                                                    setActiveFile(file)
                                                    setActiveFilepath(file.node.path)
                                                }}
                                                className={`px-2 py-1 text-xs font-medium flex items-center space-x-2 group select-none text-muted-foreground ${file.node.path === activeFile?.node.path ? 'text-black bg-white border-b-white border border-t-black' : 'border border-gray-200'} ${index === 0 ? 'border-l-0' : ''}`}
                                            >
                                                <div>
                                                    {file.node.name}
                                                </div>
                                                <div className="relative h-3 w-3">
                                                    {file.isDirty ? (
                                                        <div className="h-3 w-3 rounded-full bg-blue-300 group-hover:invisible"></div>
                                                    ) : null}
                                                    <div
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            closeFile(file);
                                                        }}
                                                        className={`rounded-full bg-gray-500 text-gray-100 w-3 h-3 flex justify-center items-center font-bold ${file.isDirty ? 'opacity-0 group-hover:opacity-100' : 'opacity-0 group-hover:opacity-100'} transition-opacity absolute top-0 left-0`}
                                                    >
                                                        <X className='h-3 w-3' />
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    <ScrollBar className='h-2' orientation="horizontal" />
                                </ScrollArea>
                            </div>
                        </div>
                        <div className='py-2 w-full h-full'>
                            <PanelGroup direction="vertical" className="h-fit">
                                {promptBoxOpen && (
                                    <PromptBox setPromptBoxOpen={setPromptBoxOpen} />
                                )}
                                <Panel className='h-full relative z-0'>
                                    <EditorContent setPromptBoxOpen={setPromptBoxOpen} containerWidth={topBarWidth as number} />
                                </Panel>
                                {showBottomPanel && (
                                    <BottomPanel
                                        rowData={rowData}
                                        gridRef={gridRef}
                                        colDefs={colDefs}
                                        runQueryPreview={runQueryPreview}
                                        queryPreviewError={queryPreviewError}
                                        isLoading={isLoading}
                                    />
                                )}
                            </PanelGroup>
                        </div>
                    </div>
                </Panel >
                {showRightSideBar && (
                    <Fragment>
                        <PanelResizeHandle className="border-l w-1 bg-transparent hover:bg-gray-300 hover:cursor-col-resize transition-colors" />
                        <Panel defaultSize={rightWidth} minSize={25} maxSize={60} onResize={setRightWidth}>
                            <div className="h-full p-4 flex items-center justify-center">Coming soon...</div>
                        </Panel>
                    </Fragment>
                )
                }
            </PanelGroup >
        </div >
    )

    return (
        <div>
            <div
                className={cn(
                    "flex h-[52px] items-center justify-center",
                    "h-[52px]"
                )}
            >
                asd
            </div>
            <Separator />
            <div>
                asd
            </div>
        </div>
    )
}

export default function EditorPage() {
    return (
        <FilesProvider>
            <LineageProvider>
                <EditorPageContent />
            </LineageProvider>
        </FilesProvider>
    )
}