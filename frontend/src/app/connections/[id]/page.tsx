import { getResource } from "../../actions/actions"
import ConnectionLayout from "../connection-layout"

export default async function ConnectionPage({ params }: { params: { id: string } }) {
    const data = await getResource(params.id)

    return (
        <div className='max-w-7xl w-full px-16 py-4'>
            <ConnectionLayout resource={data.resource} details={data.details} dbtDetails={data.dbt_details} />
        </div>
    )
}