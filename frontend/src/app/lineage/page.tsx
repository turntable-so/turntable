'use client'
import { useAppContext } from "../../contexts/AppContext";
import { Loader2 } from "lucide-react";
import { unstable_noStore as noStore } from 'next/cache';

export default function Page() {
    noStore()

    const { isLineageLoading } = useAppContext()
    return (
        <div className='w-full'>
            <div className='absolute bg-zinc-200 w-full h-screen' />
            {isLineageLoading && (
                <div className='flex items-center w-full h-screen justify-center'>
                    <Loader2 className="bg-zinc-200 h-8 w-8 animate-spin opacity-50" />
                </div>
            )}
        </div>
    )
}