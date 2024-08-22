'use client'
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ChevronLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

import DbtProjectForm from "@/components/connections/forms/dbt-project-form";
import DbtCoreLogo from "@/components/logos/dbt-core";

export default function PostgresPage() {

    const router = useRouter()

    return (
        <div className='max-w-7xl w-full px-16 py-4'>
            <Button variant='ghost' className='my-4 text-lg  flex items-center space-x-4' onClick={() => {
                router.push('/connections/new')
            }}>
                <ChevronLeft className='size-5' />
                <div className='flex space-x-1'>
                    <DbtCoreLogo />
                    <div>Connect a dbt Core project</div>
                </div>
            </Button>
            <Separator />
            <div className='flex justify-center'>
                <div className='flex justify-center w-full py-8'>
                    <DbtProjectForm />
                </div>
            </div>
        </div>
    )
}