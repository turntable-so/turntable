'use client'

import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ChevronLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

import { PowerBIIcon } from '@/lib/utils';
import PowerBIForm from "@/components/connections/forms/powerbi-form";

export default function PowerBiPage() {
    const router = useRouter()

    return (
        <div className='max-w-7xl w-full px-16 py-4'>
            <Button variant='ghost' className='my-4 text-lg  flex items-center space-x-4' onClick={() => {
                router.push('/connections/new')
            }}>
                <ChevronLeft className='size-5' />
                <div className='flex items-center space-x-2'>
                    <PowerBIIcon />
                    <div>Create a PowerBI connection</div>
                </div>
            </Button>
            <Separator />
            <div className='flex justify-center'>
                <div className='flex justify-center w-full py-8'>
                    <PowerBIForm />
                </div>
            </div>
        </div>
    )
}
