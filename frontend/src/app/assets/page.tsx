'use client'
import { AssetViewerProvider } from '@/contexts/AssetViewerContext'
import ViewerContainer from "@/components/table-viewer/viewer-container"



export default function AssetsPage() {

    return (
        <AssetViewerProvider>
            <ViewerContainer />
        </AssetViewerProvider>
    )
}
