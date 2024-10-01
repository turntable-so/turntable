'use client'
import { Tree, TreeApi } from 'react-arborist'
import { useState, useEffect, Fragment, useCallback, useRef } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { executeQueryPreview, getBranches, getFileIndex } from '../actions/actions'
import useResizeObserver from "use-resize-observer";
import { Box, File, FileText, Folder, FolderOpen, GitBranch, Loader2, PanelBottom, PanelLeft, PanelRight, Play, Plus, X } from 'lucide-react'
import Editor from '@monaco-editor/react';
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


function Node({ node, style, dragHandle }: { node: any, style: any, dragHandle: any }) {
    const { openFile } = useFiles();

    return (
        <div style={style} onClick={() => {
            if (node.isLeaf) {
                openFile(node.data);
            } else {
                node.toggle()
            }
        }} ref={dragHandle} className='hover:bg-gray-200 hover:cursor-pointer flex items-center'>
            {!node.isLeaf && (node.isOpen ? <FolderOpen className='mr-1 size-4' /> : <Folder className='mr-1 size-4' />)}
            {node.isLeaf && node.data.name.endsWith('.sql') && <Box className='mr-1 h-4 w-4' />}
            {node.isLeaf && node.data.name.endsWith('.yml') && <FileText className='mr-1 h-4 w-4' />}
            {node.isLeaf && !node.data.name.endsWith('.sql') && !node.data.name.endsWith('.yml') && <File className='mr-1 size-4' />}
            <div className='truncate'>
                {node.data.name}
            </div>
        </div>
    );
}

function EditorContent() {
    const { activeFile, updateFileContent } = useFiles();

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

    console.log('editrocontent', { activeFile })

    return (
        <Editor
            value={activeFile?.content || ''}
            onChange={(value) => {
                if (activeFile) {
                    updateFileContent(activeFile.node.path, value || '');
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
            }}
            beforeMount={(monaco) => {
                monaco.editor.defineTheme('mutedTheme', customTheme as any);
                monaco.editor.setTheme('mutedTheme');
            }}
            onMount={(editor, monaco) => {
                monaco.editor.setTheme('mutedTheme');
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
    const { ref, width, height } = useResizeObserver();
    const { files, openedFiles, activeFile, setActiveFile, closeFile } = useFiles();

    const [showLeftSideBar, setShowLeftSidebar] = useState(true)
    const [showRightSideBar, setShowRightSidebar] = useState(false)
    const [showBottomPanel, setShowBottomPanel] = useState(false)

    const [colDefs, setColDefs] = useState([])
    const [rowData, setRowData] = useState([])
    const [isLoading, setIsLoading] = useState(false)
    const gridRef = useRef<AgGridReact>(null);
    const [queryPreview, setQueryPreview] = useState<QueryPreview | null>(null)

    const treeRef = useRef<any>(null);
    const [isSearchFocused, setIsSearchFocused] = useState(false);
    const searchInputRef = useRef<HTMLInputElement>(null);

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
                    case 'k':
                        event.preventDefault();
                        console.log('Cmd+K pressed');
                        searchInputRef.current?.focus();
                        break;
                    case 'j':
                        event.preventDefault();
                        console.log('Cmd+J pressed');
                        setShowBottomPanel(!showBottomPanel)
                        break;
                }
            }
        };

        window.addEventListener('keydown', handleKeyDown);

        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, [showLeftSideBar, showRightSideBar, showBottomPanel]);


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
        if (activeFile && activeFile.content) {
            const query = activeFile.content
            const preview = await executeQueryPreview(
                query,
            )
            setQueryPreview(preview)
        }
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
            {/* <div className='bg-muted border-b-2 h-10'>
             nodes   asd
            </div> */}
            <PanelGroup direction="horizontal" className="h-fit">
                {showLeftSideBar && (
                    <Fragment>
                        <Panel defaultSize={leftWidth} minSize={15} maxSize={30} onResize={setLeftWidth} className='border-r'>
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
                                    <div className="h-full" ref={ref}>
                                        <Tree
                                            height={height}
                                            width={width}
                                            data={files}
                                            openByDefault={false}
                                            indent={12}
                                            ref={treeRef}
                                        >
                                            {Node as any}
                                        </Tree>
                                    </div>
                                </TabsContent>
                                <TabsContent value="branch">Branhce</TabsContent>
                            </Tabs>
                        </Panel>
                        <PanelResizeHandle className="w-1 bg-transparent hover:bg-gray-300 hover:cursor-col-resize  transition-colors" />
                    </Fragment>
                )}
                <Panel>
                    <div className="h-full bg-white">
                        <div
                            className={cn(
                                "flex h-[52px] items-center justify-center",
                                "h-[52px]"
                            )}
                        >
                            <div className="flex items-center w-full px-4">
                                <div className="w-1/4">
                                    {/* Left column content */}
                                </div>
                                <div className="w-1/2 relative">
                                    <Input
                                        ref={searchInputRef}
                                        type="text"
                                        placeholder="Search files... (⌘K)"
                                        className="w-full pl-10 pr-4 py-2 rounded-md bg-muted focus:outline-none focus:ring-2 focus:ring-gray-400"
                                        onFocus={() => setIsSearchFocused(true)}
                                        onBlur={() => setIsSearchFocused(false)}
                                    />

                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                        </svg>
                                    </div>
                                </div>
                                <div className="w-1/4">
                                    <div className="flex justify-end space-x-2">
                                        <TooltipProvider>
                                            <Tooltip>
                                                <TooltipTrigger asChild>
                                                    <Button
                                                        variant={showLeftSideBar ? "secondary" : "ghost"}
                                                        size="icon"
                                                        onClick={() => setShowLeftSidebar(!showLeftSideBar)}
                                                    >
                                                        <PanelLeft className="h-4 w-4" />
                                                    </Button>
                                                </TooltipTrigger>
                                                <TooltipContent>
                                                    <p>Toggle Side Bar (⌘B)</p>
                                                </TooltipContent>
                                            </Tooltip>
                                            <Tooltip>
                                                <TooltipTrigger asChild>
                                                    <Button
                                                        variant={showBottomPanel ? "secondary" : "ghost"}
                                                        size="icon"
                                                        onClick={() => setShowBottomPanel(!showBottomPanel)}
                                                    >
                                                        <PanelBottom className="h-4 w-4" />
                                                    </Button>
                                                </TooltipTrigger>
                                                <TooltipContent>
                                                    <p>Toggle Bottom Panel (⌘J)</p>
                                                </TooltipContent>
                                            </Tooltip>
                                            <Tooltip>
                                                <TooltipTrigger asChild>
                                                    <Button
                                                        variant={showRightSideBar ? "secondary" : "ghost"}
                                                        size="icon"
                                                        onClick={() => setShowRightSidebar(!showRightSideBar)}
                                                    >
                                                        <PanelRight className="h-4 w-4" />
                                                    </Button>
                                                </TooltipTrigger>
                                                <TooltipContent>
                                                    <p>Toggle AI Pane (⌘^B)</p>
                                                </TooltipContent>
                                            </Tooltip>
                                        </TooltipProvider>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <Separator />
                        <div className='hover:cursor-pointer h-8 border-b-2 flex items-center space-x-2 py-4'>
                            <div className='ml-1  hover:bg-gray-200 bg-muted w-8 h-6 rounded-md flex items-center justify-center'>
                                <Plus className='size-3' />
                            </div>
                            <div className='overflow-x-scroll flex space-x-0'>
                                {openedFiles.map((file: OpenedFile) => (
                                    <div
                                        key={file.node.path}
                                        onClick={() => setActiveFile(file)}
                                        className={`text-sm font-medium border-x-2  px-2 py-1 flex items-center space-x-2 group select-none ${file.node.path === activeFile?.node.path ? 'bg-muted' : ''}`}
                                    >
                                        <div>
                                            {file.node.name}
                                        </div>
                                        <div onClick={() => closeFile(file)} className='rounded-full bg-gray-500 text-white w-3 h-3 flex justify-center items-center font-bold opacity-0 group-hover:opacity-100 transition-opacity'>
                                            <X className='h-2 w-2' />
                                        </div>
                                    </div>
                                ))}
                            </div>

                        </div>
                        <div className='py-2 w-full h-full'>
                            <PanelGroup direction="vertical" className="h-fit">
                                <Panel>
                                    <EditorContent />
                                </Panel>
                                {showBottomPanel && (
                                    <Fragment>
                                        <PanelResizeHandle className="h-1 bg-gray hover:bg-gray-300 hover:cursor-col-resize  transition-colors" />
                                        <div className='h-10 bg-muted border-t-2 flex justify-end items-center px-4'>
                                            <Button size='sm'
                                                onClick={runQueryPreview}
                                                disabled={isLoading}
                                            >
                                                {isLoading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Play className="h-4 w-4 mr-2" />}
                                                Preview Query
                                            </Button>
                                        </div>
                                        <Panel defaultSize={40} className='border-t flex items-center justify-center'>

                                            <div className="flex flex-col w-full h-full flex-grow-1">
                                                <AgGridReact
                                                    className="ag-theme-custom"
                                                    ref={gridRef}
                                                    suppressRowHoverHighlight={true}
                                                    columnHoverHighlight={true}
                                                    rowData={rowData}
                                                    pagination={true}
                                                    // @ts-ignore
                                                    columnDefs={colDefs}
                                                />
                                            </div>
                                        </Panel>
                                    </Fragment>
                                )}
                            </PanelGroup>
                        </div>
                    </div>
                </Panel>
                {showRightSideBar && (
                    <Fragment>
                        <PanelResizeHandle className="border-l w-1 bg-transparent hover:bg-gray-300 hover:cursor-col-resize transition-colors" />
                        <Panel defaultSize={rightWidth} minSize={25} maxSize={60} onResize={setRightWidth}>
                            <div className="h-full p-4 flex items-center justify-center">Coming soon...</div>
                        </Panel>
                    </Fragment>
                )}
            </PanelGroup>
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
            <EditorPageContent />
        </FilesProvider>
    )
}