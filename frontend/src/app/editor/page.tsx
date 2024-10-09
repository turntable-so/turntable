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

const DbtLogo = () => (
    <svg
        width="14px"
        height="14px"
        viewBox="0 0 256 256"
        version="1.1"
        preserveAspectRatio="xMidYMid"
    >
        <g>
            <path
                d="M245.121138,10.6473813 C251.139129,16.4340053 255.074133,24.0723342 256,32.4050489 C256,35.8769778 255.074133,38.1917867 252.990862,42.5895822 C250.907876,46.9873778 225.215147,91.4286933 217.57696,103.696213 C213.179164,110.871609 210.864356,119.435947 210.864356,127.768462 C210.864356,136.3328 213.179164,144.6656 217.57696,151.840996 C225.215147,164.108516 250.907876,208.781084 252.990862,213.179164 C255.074133,217.57696 256,219.659947 256,223.131876 C255.074133,231.464676 251.370667,239.103147 245.352676,244.658347 C239.565938,250.676338 231.927751,254.611342 223.826489,255.305671 C220.35456,255.305671 218.039751,254.379804 213.873493,252.296533 C209.706951,250.213262 164.340053,225.215147 152.072249,217.57696 C151.146382,217.113884 150.220516,216.419556 149.063396,215.95648 L88.4195556,180.079502 C89.8082133,191.652693 94.9006222,202.763093 103.233138,210.864356 C104.853618,212.484551 106.473813,213.873493 108.325547,215.262151 C106.936604,215.95648 105.316409,216.651093 103.927751,217.57696 C91.6599467,225.215147 46.9873778,250.907876 42.5895822,252.990862 C38.1917867,255.074133 36.1085156,256 32.4050489,256 C24.0723342,255.074133 16.4340053,251.370667 10.8788338,245.352676 C4.86075733,239.565938 0.925858133,231.927751 0,223.594951 C0.231464676,220.123022 1.1573248,216.651093 3.00905244,213.641956 C5.09223822,209.24416 30.7848533,164.571307 38.42304,152.303787 C42.82112,145.128391 45.1356444,136.795591 45.1356444,128.231538 C45.1356444,119.6672 42.82112,111.3344 38.42304,104.159004 C30.7848533,91.4286933 4.86075733,46.75584 3.00905244,42.3580444 C1.1573248,39.3489067 0.231464676,35.8769778 0,32.4050489 C0.925858133,24.0723342 4.62930489,16.4340053 10.6473813,10.6473813 C16.4340053,4.62930489 24.0723342,0.925858133 32.4050489,0 C35.8769778,0.231464676 39.3489067,1.1573248 42.5895822,3.00905244 C46.2930489,4.62930489 78.9293511,23.6094009 96.28928,33.7939911 L100.224284,36.1085156 C101.612942,37.0343822 102.770347,37.7287111 103.696213,38.1917867 L105.547947,39.3489067 L167.348907,75.9204978 C165.960249,62.0324978 158.784853,49.3019022 147.674453,40.7378489 C149.063396,40.04352 150.683591,39.3489067 152.072249,38.42304 C164.340053,30.7848533 209.012622,4.86075733 213.410418,3.00905244 C216.419556,1.1573248 219.891484,0.231464676 223.594951,0 C231.696213,0.925858133 239.334684,4.62930489 245.121138,10.6473813 Z M131.240391,144.434062 L144.434062,131.240391 C146.285796,129.388658 146.285796,126.611342 144.434062,124.759609 L131.240391,111.565938 C129.388658,109.714204 126.611342,109.714204 124.759609,111.565938 L111.565938,124.759609 C109.714204,126.611342 109.714204,129.388658 111.565938,131.240391 L124.759609,144.434062 C126.379804,146.054258 129.388658,146.054258 131.240391,144.434062 Z"
                fill="#FF694A"
            ></path>
        </g>
    </svg>
);



function Node({ node, style, dragHandle, tree }: { node: any, style: any, dragHandle: any, tree: any }) {
    const { openFile, createFileAndRefresh, deleteFileAndRefresh, closeFile } = useFiles();
    const [showOptions, setShowOptions] = useState(false)

    const handleCreateFile = async (e: React.MouseEvent) => {
        e.stopPropagation();
        const newFileName = prompt("Enter new file name:");
        if (newFileName) {
            const newPath = `${node.data.path}/${newFileName}`;
            await createFileAndRefresh(newPath, ''); // Call your backend API to create the file
            openFile({
                name: newFileName,
                path: newPath,
                type: 'file'
            });
        }
    };


    const handleDelete = async (e: React.MouseEvent) => {
        e.stopPropagation();
        if (confirm(`Are you sure you want to delete ${node.data.name}?`)) {
            await deleteFileAndRefresh(node.data.path);
            closeFile(node.data.path);
        }
    };

    // const handleRename = async (e: React.MouseEvent) => {
    //     e.stopPropagation();
    //     const newName = prompt("Enter new name:", node.data.name);
    //     if (newName && newName !== node.data.name) {
    //         const newPath = node.data.path.replace(node.data.name, newName);
    //         await renameFile(node.data.path, newPath);
    //         node.submit(newName);
    //     }
    // };


    // const handleCreateFolder = async (e: React.MouseEvent) => {
    //     e.stopPropagation();
    //     const newFolderName = prompt("Enter new folder name:");
    //     if (newFolderName) {
    //         const newPath = `${node.data.path}/${newFolderName}`;
    //         await createFile(newPath, '', true); // Call your backend API to create the folder
    //         tree.create({
    //             parentId: node.id,
    //             type: 'directory',
    //             data: { name: newFolderName, path: newPath }
    //         });
    //     }
    // };

    return (
        <div style={style} onClick={() => {
            if (node.isLeaf) {
                openFile(node.data);
            } else {
                node.toggle()
            }
        }} ref={dragHandle} className={`${node.isSelected ? 'font-medium bg-accent text-accent-foreground' : ''} hover:bg-accent hover:cursor-pointer flex items-center`}>
            {!node.isLeaf && (node.isOpen ? <ChevronDown className='mr-1 size-4' /> : <ChevronRight className='mr-1 size-4' />)}
            {node.isLeaf && node.data.name.endsWith('.sql') && <div className={`mr-1 ${node.isSelected ? 'opacity-100' : 'opacity-70'}`}><DbtLogo /></div>}
            {node.isLeaf && node.data.name.endsWith('.yml') && <FileText className='mr-1 h-4 w-4' />}
            {node.isLeaf && !node.data.name.endsWith('.sql') && !node.data.name.endsWith('.yml') && <File className='mr-1 size-4' />}
            {node.isEditing ? (
                <input
                    type="text"
                    defaultValue={node.data.name}
                    onFocus={(e) => e.currentTarget.select()}
                    onBlur={() => node.reset()}
                    onKeyDown={(e) => {
                        if (e.key === "Escape") node.reset();
                        if (e.key === "Enter") node.submit(e.currentTarget.value);
                    }}
                    autoFocus
                />
            ) : (
                <div className='w-full flex items-center justify-between group'>
                    <div className='truncate'>
                        {node.data.name}
                    </div>
                    <div className='flex items-center opacity-0 group-hover:opacity-100 transition-opacity'>
                        <Popover open={showOptions} onOpenChange={setShowOptions}>
                            <PopoverTrigger asChild>
                                <div
                                    className='text-muted-foreground text-xs hover:cursor-pointer hover:text-foreground relative'
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setShowOptions(!showOptions);
                                    }}
                                >
                                    <Ellipsis className='mr-1 size-4' />
                                </div>
                            </PopoverTrigger>
                            <PopoverContent className="w-40 p-0" onClick={(e) => e.stopPropagation()}>
                                <div className='w-full'>
                                    {/* <Button className='w-full' variant="ghost" size="sm" onClick={handleRename}>
                                        <Pencil className="mr-2 h-3 w-3" />
                                        Rename
                                    </Button> */}
                                    <Button className='w-full' variant="ghost" size="sm" onClick={handleDelete}>
                                        <Trash className="mr-2 h-3 w-3" />
                                        Delete
                                    </Button>
                                </div>
                            </PopoverContent>
                        </Popover>
                        {!node.isLeaf && (
                            <>
                                <div
                                    className='text-muted-foreground text-xs hover:cursor-pointer hover:text-foreground relative'
                                    onClick={handleCreateFile}
                                >
                                    <Plus className='mr-1 size-4' />
                                </div>
                                {/* <div
                                    className='text-muted-foreground text-xs hover:cursor-pointer hover:text-foreground relative'
                                    onClick={handleCreateFolder}
                                >
                                    <Folder className='mr-1 size-4' />
                                    <span>New Folder</span>
                                </div> */}
                            </>
                        )}
                    </div>

                </div>
            )}
        </div>
    );
}

function EditorContent({ setPromptBoxOpen, containerWidth }: { setPromptBoxOpen: (open: boolean) => void, containerWidth: number }) {
    const { activeFile, updateFileContent, saveFile, activeFilepath } = useFiles();

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

    console.log({ activeFile })

    if (activeFile?.view === 'diff') {
        return (
            <DiffEditor
                original={activeFile?.diff?.original || ''}
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


    return (
        <Editor
            key={activeFile?.node.path}
            value={activeFile?.content || ''}
            onChange={(value) => {
                console.log('onchange', { value, activeFile })
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
            width={containerWidth - 2}
            beforeMount={(monaco) => {
                monaco.editor.defineTheme('mutedTheme', customTheme as any);
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
        if (activeFile && activeFile.content) {
            const query = activeFile.content
            const preview = await executeQueryPreview(
                query,
            )
            setQueryPreview(preview)
        }
    }

    console.log({
        activeFilepath
    })


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

    const onCreate = async ({ parentId, index, type }: { parentId: string, index: number, type: string }) => {

    };
    const onRename = ({ id, name }: { id: string, name: string }) => {
        console.log('renaming!', { id, name })
    };
    // noop
    const onMove = ({ dragIds, parentId, index }: { dragIds: string[], parentId: string, index: number }) => {
        console.log('moving!', { dragIds, parentId, index })
    };

    const onDelete = ({ ids }: { ids: string[] }) => {
        console.log('deleting!', { ids, })
    };



    return (
        <div className='flex flex-col h-screen'>
            <PanelGroup direction="horizontal" className="h-fit">
                {showLeftSideBar && (
                    <Fragment>
                        <Panel defaultSize={leftWidth} minSize={15} maxSize={30} onResize={setLeftWidth} className='border-r bg-muted/50 text-gray-600'>
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
                        </Panel>
                        <PanelResizeHandle className="relative w-1 bg-transparent hover:bg-gray-300 hover:cursor-col-resize  transition-colors" />
                    </Fragment>
                )}
                <Panel>
                    <div className="h-full bg-white" ref={topBarRef}>
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
                                <div className="w-full relative z-50">
                                    <Input
                                        ref={searchInputRef}
                                        value={filesearchQuery}
                                        onChange={(e) => setFilesearchQuery(e.target.value)}
                                        type="text"
                                        placeholder="Search files... (⌘P)"

                                        className={`${isSearchFocused ? 'rounded-b-none' : 'rounded-md'} w-full pl-10 pr-4 py-2 bg-muted focus:outline-none focus:ring-2 focus:ring-gray-400`}
                                        onFocus={() => setIsSearchFocused(true)}
                                        onBlur={() => {
                                            setFilesearchQuery('')
                                            setTimeout(() => {
                                                setIsSearchFocused(false)
                                            }, 100)
                                        }}
                                    />
                                    {isSearchFocused && (
                                        <div className='w-full flex-grow mr-[4px] absolute h-[350px] border-l border-r border-b rounded-b-md  border-black  overflow-y-scroll bg-muted'>
                                            <FileSearchCommand query={filesearchQuery} onFileNodeSelect={(fileNode: FileNode) => {
                                                setIsSearchFocused(false)
                                                openFile(fileNode)
                                                setFilesearchQuery('')
                                            }} />
                                        </div>
                                    )}

                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                        </svg>
                                    </div>
                                </div>
                                <div className="w-1/4">
                                    <div className="flex justify-end space-x-2">
                                        <TooltipProvider delayDuration={0}>
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
                                                <TooltipContent >
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
                            <div className='w-full' style={{
                                maxWidth: topBarWidth ? topBarWidth - 50 : '100%'
                            }}>
                                <ScrollArea className='w-full flex whitespace-nowrap overflow-x-scroll'>
                                    <div className='w-max flex overflow-x-scroll'>
                                        {openedFiles.map((file: OpenedFile) => (
                                            <div
                                                key={file.node.path}
                                                onClick={() => {
                                                    setActiveFile(file)
                                                    setActiveFilepath(file.node.path)
                                                }}
                                                className={`text-sm font-medium border-x-2  px-2 py-1 flex items-center space-x-2 group select-none ${file.node.path === activeFile?.node.path ? 'bg-muted' : ''}`}
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
                                                        className={`rounded-full bg-gray-500 text-white w-3 h-3 flex justify-center items-center font-bold ${file.isDirty ? 'opacity-0 group-hover:opacity-100' : 'opacity-0 group-hover:opacity-100'} transition-opacity absolute top-0 left-0`}
                                                    >
                                                        <X className='h-2 w-2' />
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
                                    <Fragment>
                                        <PanelResizeHandle className="h-1 bg-gray hover:bg-gray-300 hover:cursor-col-resize  transition-colors" />
                                        <div className='h-10 bg-muted border-t-2 flex justify-end items-center px-4'>
                                            <Button size='sm'
                                                onClick={runQueryPreview}
                                                disabled={isLoading}
                                                variant='outline'
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
            <EditorPageContent />
        </FilesProvider>
    )
}