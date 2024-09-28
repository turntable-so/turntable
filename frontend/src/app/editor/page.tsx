'use client'
import { Tree } from 'react-arborist'
import { useState, useEffect } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { getBranches, getFileIndex } from '../actions/actions'
import useResizeObserver from "use-resize-observer";
import { Box, File, FileText, Folder, FolderOpen } from 'lucide-react'

type FileNode = {
    name: string
    path: string
    type: 'file' | 'directory'
    children: FileNode[]
}

function Node({ node, style, dragHandle, handleNodeClick }) {
    /* This node instance can do many things. See the API reference. */
    return (
        <div style={style} onClick={() => {
            if (node.isLeaf) {
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

const data = [
    { id: "1", name: "Unread" },
    { id: "2", name: "Threads" },
    {
        id: "3",
        name: "Chat Rooms",
        children: [
            { id: "c1", name: "General" },
            { id: "c2", name: "Random" },
            { id: "c3", name: "Open Source Projects" },
        ],
    },
    {
        id: "4",
        name: "Direct Messages",
        children: [
            { id: "d1", name: "Alice" },
            { id: "d2", name: "Bob" },
            { id: "d3", name: "Charlie" },
        ],
    },
];

export default function EditorPage() {
    const [leftWidth, setLeftWidth] = useState(20)
    const [rightWidth, setRightWidth] = useState(20)

    const [branches, setBranches] = useState([])
    const [activeBranch, setActiveBranch] = useState('')
    const [files, setFiles] = useState([])
    const [dirtyFiles, setDirtyFiles] = useState([])
    const { ref, width, height } = useResizeObserver();
    const [openFile, setOpenFile] = useState(null)


    useEffect(() => {
        const fetchBranches = async () => {
            const {
                active_branch, branches
            } = await getBranches()

            setActiveBranch(active_branch)
            setBranches(branches)
        }
        fetchBranches()
    }, [])

    const handleNodeClick = (e: any) => {
        console.log(e.target)
    }

    useEffect(() => {
        const fetchFiles = async () => {
            const {
                dirty_changes,
                file_index
            } = await getFileIndex()
            const fileIndex = file_index.map((file: FileNode) => ({ ...file }))
            setFiles(fileIndex)
            setDirtyFiles(dirty_changes)
        }
        fetchFiles()
    }, [])

    console.log({ files })

    return (
        <div className='flex flex-col h-screen'>
            <div className='bg-muted border-b-2 h-10'>
                asd
            </div>
            <PanelGroup direction="horizontal" className="h-fit">
                <Panel defaultSize={leftWidth} minSize={15} maxSize={30} onResize={setLeftWidth}>
                    <div className="h-full bg-gray-100 p-4" ref={ref}>
                        <Tree height={height} width={width} data={files} onClick={handleNodeClick} openByDefault={false}>
                            {Node}
                        </Tree>
                    </div>
                </Panel>
                <PanelResizeHandle className="w-1 bg-transparent hover:bg-gray-300 hover:cursor-col-resize  transition-colors" />
                <Panel>
                    <div className="h-full bg-white p-4">Main Content</div>
                </Panel>
                <PanelResizeHandle className="w-1 bg-transparent hover:bg-gray-300 hover:cursor-col-resize transition-colors" />
                <Panel defaultSize={rightWidth} minSize={15} maxSize={30} onResize={setRightWidth}>
                    <div className="h-full bg-gray-100 p-4">Right Sidebar</div>
                </Panel>
            </PanelGroup>
        </div>
    )
}