'use client'
import React from "react"
import { getResource } from "../../actions/actions"
import ConnectionLayout from "../connection-layout"

export default function ConnectionPage({ params }: { params: { id: string } }) {
    const [data, setData] = React.useState<any>(null)

    const fetchResources = async () => {
        const value = await getResource(params.id)
        setData(value)
    }
    React.useEffect(() => {
        fetchResources();
    }, [])

    return (
        <div className='max-w-7xl w-full px-16 py-4'>
            {data && <ConnectionLayout resource={data.resource} details={data.details} dbtDetails={data.dbt_details} />}
        </div>
    )
}