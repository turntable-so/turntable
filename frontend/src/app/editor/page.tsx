'use client'
import { Tree } from 'react-arborist'
import { useState, useEffect } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { executeQueryPreview, getBranches, getFileIndex } from '../actions/actions'
import useResizeObserver from "use-resize-observer";
import { Box, File, FileText, Folder, FolderOpen, GitBranch, PanelBottom, PanelLeft, PanelRight, Plus, X } from 'lucide-react'
import Editor from '@monaco-editor/react';
import { FilesProvider, useFiles, FileNode, OpenedFile } from '../contexts/FilesContext';
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'

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
                theme: 'vs-light',
                fontSize: 14,
                lineNumbersMinChars: 3,
            }}
            beforeMount={(monaco) => {
                monaco.editor.defineTheme('muted-theme', {
                    base: 'vs',
                    inherit: true,
                    rules: [],
                    colors: {
                        'editorLineNumber.foreground': '#9CA3AF', // Tailwind gray-400
                    },
                });
            }}
            theme="muted-theme"
        />
    );
}

function EditorPageContent() {
    const [leftWidth, setLeftWidth] = useState(20)
    const [rightWidth, setRightWidth] = useState(20)
    const [branches, setBranches] = useState([])
    const [activeBranch, setActiveBranch] = useState('')
    const { ref, width, height } = useResizeObserver();
    const { files, openedFiles, activeFile, setActiveFile, closeFile } = useFiles();


    useEffect(() => {
        const fetchBranches = async () => {
            const { active_branch, branches } = await getBranches()
            setActiveBranch(active_branch)
            setBranches(branches)
        }
        fetchBranches()
    }, [])

    console.log({ files, activeFile })

    const runQueryPreview = async () => {
        const query = "select * from {{ ref('raw_products') }}"
        const data = await executeQueryPreview(
            query,
        )
        console.log({ data })
    }

    return (
        <div className='flex flex-col h-screen'>
            {/* <div className='bg-muted border-b-2 h-10'>
             nodes   asd
            </div> */}
            <PanelGroup direction="horizontal" className="h-fit">
                <Panel defaultSize={leftWidth} minSize={15} maxSize={30} onResize={setLeftWidth} className='border-r'>
                    <Tabs defaultValue="files" className="">
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
                        <TabsContent value="files">
                            <div className="h-full   p-4" ref={ref}>
                                <Tree height={height} width={width} data={files} openByDefault={false} >
                                    {Node}
                                </Tree>
                            </div>
                        </TabsContent>
                        <TabsContent value="branch">Branhce</TabsContent>
                    </Tabs>
                </Panel>
                <PanelResizeHandle className="w-1 bg-transparent hover:bg-gray-300 hover:cursor-col-resize  transition-colors" />
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
                                        type="text"
                                        placeholder="Search files..."
                                        className="w-full pl-10 pr-4 py-2 rounded-md bg-muted focus:outline-none focus:ring-2 focus:ring-gray-400"
                                    />
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                        </svg>
                                    </div>
                                </div>
                                <div className="w-1/4">
                                    <div className="flex justify-end space-x-2">
                                        <Button variant="ghost" size="icon">
                                            <PanelLeft className="h-4 w-4" />
                                        </Button>
                                        <Button variant="ghost" size="icon">
                                            <PanelBottom className="h-4 w-4" />
                                        </Button>
                                        <Button variant="ghost" size="icon">
                                            <PanelRight className="h-4 w-4" />
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <Separator />
                        <div className='hover:cursor-pointer h-8 border-b-2 flex items-center space-x-4 py-4'>
                            <div className='ml-1  hover:bg-gray-200 bg-muted w-8 h-6 rounded-md flex items-center justify-center'>
                                <Plus className='size-3' />
                            </div>
                            <div className='overflow-x-scroll flex space-x-2'>
                                {openedFiles.map((file: OpenedFile) => (
                                    <div
                                        key={file.node.path}
                                        onClick={() => setActiveFile(file)}
                                        className={`text-sm font-medium border  px-2 py-1 rounded-md flex items-center space-x-2 group select-none ${file.node.path === activeFile?.node.path ? 'bg-muted' : ''}`}
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
                                <PanelResizeHandle className="h-1 bg-gray hover:bg-gray-300 hover:cursor-col-resize  transition-colors" />
                                <Panel defaultSize={30} className='border-t flex items-center justify-center'>
                                    <Button onClick={runQueryPreview}>
                                        Run Query
                                    </Button>
                                </Panel>
                            </PanelGroup>
                        </div>
                    </div>
                </Panel>
                <PanelResizeHandle className="w-1 bg-transparent hover:bg-gray-300 hover:cursor-col-resize transition-colors" />
                {/* <Panel defaultSize={rightWidth} minSize={15} maxSize={30} onResize={setRightWidth}>
                    <div className="h-full bg-gray-100 p-4">Right Sidebar</div>
                </Panel> */}
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