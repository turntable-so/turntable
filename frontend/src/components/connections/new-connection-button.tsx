'use client'
import { Plus } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { Button } from '../ui/button'


export default function NewConnectionButton() {
    const router = useRouter()

    return (
        <Button onClick={() => {
            router.push('/connections/new')
        }} className='rounded-full space-x-2'>
            <Plus className='size-4' />
            <div>
                New connection
            </div>
        </Button>
    )
}