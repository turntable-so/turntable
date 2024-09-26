'use client'
import { Tree } from 'react-arborist'
import { useState, useEffect } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { getBranches } from '../actions/actions'

export default function EditorPage() {
    const [leftWidth, setLeftWidth] = useState(20)
    const [rightWidth, setRightWidth] = useState(20)

    useEffect(() => {
        const fetchBranches = async () => {
            const branches = await getBranches()
            console.log({ branches })
        }
        fetchBranches()
    }, [])

    return (
        <PanelGroup direction="horizontal" className="h-screen">
            <Panel defaultSize={leftWidth} minSize={15} maxSize={30} onResize={setLeftWidth}>
                <div className="h-full bg-gray-100 p-4">Left Sidebar</div>
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
    )
}