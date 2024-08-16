'use client'
import { Button } from "@/components/ui/button";
import { useRouter } from 'next/navigation'
import { ChevronLeft, Plus } from 'lucide-react'
import { Separator } from "@/components/ui/separator";

import { PostgresLogo } from "@/components/connections/connection-options";
import PostgresForm from "@/components/connections/forms/postgres-form";

export default function PostgresPage() {

    const router = useRouter()

    return (
        <div className='max-w-7xl w-full px-16 py-4'>
            <Button variant='ghost' className='my-4 text-lg  flex items-center space-x-4' onClick={() => {
                router.push('/connections/new')
            }}>
                <ChevronLeft className='size-5' />
                <div className='flex space-x-1'>
                    <PostgresLogo />
                    <div>Create a PostgresSQL connection</div>
                </div>
            </Button>
            <Separator />
            <div className='flex justify-center'>
                <div className='flex justify-center w-full py-8'>
                    <PostgresForm />
                </div>
            </div>
        </div>
    )
}