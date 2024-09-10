'use client'
import { Box, DatabaseZap, Search, Tag } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { ReactNode, useEffect, useState } from "react"

import AssetViewDataTable from "@/components/ui/data-table"
import { Asset } from "@/components/ui/schema"
import { columns } from "@/components/ui/data-table-columns"

import { getAssets } from "../actions/actions"
import { useAppContext } from '@/contexts/AppContext'
import { AssetViewerProvider, useAssetViewer } from '@/contexts/AssetViewerContext'




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
