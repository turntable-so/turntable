'use client'
import { Button } from '../../components/ui/button'
import { LoaderButton } from '../../components/ui/LoadingSpinner'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { createSource } from '../actions/actions'



export default function CreateNotebookButton() {
    const router = useRouter()

    const [isLoading, setIsLoading] = useState<boolean>(false)

    const onNewNotebookClick = async () => {
        setIsLoading(true)
        const source = await createSource()
        if (source) {
            router.push(`/sources/${source.id}`)
        }
    }

    return (
        <LoaderButton isDisabled={true} onClick={onNewNotebookClick} isLoading={isLoading}>
            New
        </LoaderButton>
    )
}