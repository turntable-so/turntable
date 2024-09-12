'use client'
import { ReactNode } from "react"

import AssetViewDataTable from "@/components/ui/data-table"

import { AssetViewerProvider } from '@/contexts/AssetViewerContext'




type Option = {
    value: string, label: string, icon?: ReactNode
}


export default function AssetsPage() {



    return (
        <AssetViewerProvider>
            <div className='max-w-7xl w-full px-8 py-4 mt-4 mb-8'>
                <AssetViewDataTable />
            </div>
        </AssetViewerProvider>
    )
}
