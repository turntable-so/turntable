'use client'
import { ReactNode } from "react"

import AssetViewDataTable from "@/components/ui/data-table"

import { AssetViewerProvider } from '@/contexts/AssetViewerContext'



export default function AssetsPage() {

    return (
        <AssetViewerProvider>
            <div className='w-full px-8 py-4 mt-4 mb-8'>
                <AssetViewDataTable />
            </div>
        </AssetViewerProvider>
    )
}
