import { getLineage } from '../../actions/actions'
import { LineageView } from '../../../components/lineage/LineageView'

export default async function LineagePage({ params }: { params: { id: string } }) {


    const { lineage, root_asset } = await getLineage({ nodeId: params.id, successor_depth: 1, predecessor_depth: 1, lineage_type: 'all' })
    return (<div className='w-full h-screen overflow-y-scroll'>
        <div className=''>
            {/* <ErrorBoundary
                FallbackComponent={() => <div>Something went wrong</div>}
                onError={e => console.error(e)}> */}
            <LineageView lineage={lineage} rootAsset={root_asset} />
            {/* </ErrorBoundary> */}
        </div>
    </div>)
} 