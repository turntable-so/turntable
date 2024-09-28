'use client'
import { Tree } from 'react-arborist'
import { useState, useEffect } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { getBranches, getFileIndex } from '../actions/actions'
import useResizeObserver from "use-resize-observer";
import { Box, File, FileText, Folder, FolderOpen, Plus, X } from 'lucide-react'
import Editor from '@monaco-editor/react';
import { FilesProvider, useFiles, FileNode, OpenedFile } from '../contexts/FilesContext';
import { Button } from '@/components/ui/button'

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

    return (
        <div className='flex flex-col h-screen'>
            {/* <div className='bg-muted border-b-2 h-10'>
             nodes   asd
            </div> */}
            <PanelGroup direction="horizontal" className="h-fit">
                <Panel defaultSize={leftWidth} minSize={15} maxSize={30} onResize={setLeftWidth}>
                    <div className="h-full bg-gray-100 p-4" ref={ref}>
                        <Tree height={height} width={width} data={files} openByDefault={false} >
                            {Node}
                        </Tree>
                    </div>
                </Panel>
                <PanelResizeHandle className="w-1 bg-transparent hover:bg-gray-300 hover:cursor-col-resize  transition-colors" />
                <Panel>
                    <div className="h-full bg-white">
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
                                <PanelResizeHandle className="h-2 bg-gray hover:bg-gray-300 hover:cursor-col-resize  transition-colors" />
                                <Panel defaultSize={30} className='border-t-2'>
                                    <div>
                                        sd
                                    </div>
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