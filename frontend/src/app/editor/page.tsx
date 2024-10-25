'use client'
import { Tree, TreeApi } from 'react-arborist'
import { useState, useEffect, Fragment, useCallback, useRef } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { executeQueryPreview, getBranches, infer } from '../actions/actions'
import useResizeObserver from "use-resize-observer";
import { Box, Check, ChevronDown, ChevronRight, CircleArrowUp, Ellipsis, File, FileText, Folder, FolderOpen, GitBranch, Loader2, PanelBottom, PanelLeft, PanelRight, Pencil, Play, Plus, Sparkles, Trash, X } from 'lucide-react'
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
import AiSidebarChat from '@/components/editor/ai-sidebar-chat'
import PromptBox from '@/components/editor/single-file-edit-prompt-popover'

import EditorSidebar from '@/components/editor/editor-sidebar'
import FileTabs from '@/components/editor/file-tabs'
import { useLayoutContext } from '../contexts/LayoutContext'



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
                new tab experience coming soon
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
    const [leftWidth, setLeftWidth] = useState(15)
    const [rightWidth, setRightWidth] = useState(20)
    const [branches, setBranches] = useState([])
    const [activeBranch, setActiveBranch] = useState('')
    const { ref: treeContainerRef, width: treeWidth, height: treeHeight } = useResizeObserver();
    const { ref: topBarRef, width: topBarWidth, height: topBarHeight } = useResizeObserver();

    const { files, openedFiles, activeFile, openFile, setActiveFile, activeFilepath, closeFile, setActiveFilepath } = useFiles();

    const { sidebarLeftShown, sidebarRightShown, bottomPanelShown, setSidebarLeftShown, setSidebarRightShown, setBottomPanelShown, } = useLayoutContext();


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
                            setSidebarRightShown(!sidebarRightShown)

                        } else {
                            console.log('Cmd+B pressed');
                            setSidebarLeftShown(!sidebarLeftShown)
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
                        setBottomPanelShown(!bottomPanelShown)
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
    }, [sidebarLeftShown, sidebarRightShown, bottomPanelShown, isSearchFocused, selectedIndex]);


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
                {sidebarLeftShown && (
                    <Panel defaultSize={leftWidth} minSize={15} maxSize={30} onResize={setLeftWidth} className='border-r  text-gray-600'>
                        <EditorSidebar />
                    </Panel>
                )}
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
                        <FileTabs
                            topBarRef={topBarRef as any}
                            topBarWidth={topBarWidth as number}
                        />
                        <div className='py-2 w-full h-full'>
                            <PanelGroup direction="vertical" className="h-fit">
                                {promptBoxOpen && (
                                    <PromptBox setPromptBoxOpen={setPromptBoxOpen} />
                                )}
                                <Panel className='h-full relative z-0'>
                                    <EditorContent setPromptBoxOpen={setPromptBoxOpen} containerWidth={topBarWidth as number} />
                                </Panel>
                                {bottomPanelShown && (
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
                {sidebarRightShown && (
                    <Fragment>
                        <PanelResizeHandle className="border-l w-1 bg-transparent hover:bg-gray-300 hover:cursor-col-resize transition-colors" />
                        <Panel defaultSize={rightWidth} minSize={25} maxSize={60} onResize={setRightWidth}>
                            <div className="h-full overflow-y-scroll">
                                <AiSidebarChat />
                            </div>
                        </Panel >
                    </Fragment >
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