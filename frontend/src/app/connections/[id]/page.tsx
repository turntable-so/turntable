'use client'
import React from "react"
import { getResource } from "../../actions/actions"
import ConnectionLayout from "../connection-layout"

export default function ConnectionPage({ params }: { params: { id: string } }) {
    const [resource, setResource] = React.useState(null)

    const fetchResources = async () => {
        const data = await getResource(params.id)
        setResource(data)
    }
    React.useEffect(() => {
        fetchResources();
    }, [])

    return (
        <div className='max-w-7xl w-full px-16 py-4'>
            {resource && <ConnectionLayout resource={resource} details={resource.details} />}
        </div>
    )
}