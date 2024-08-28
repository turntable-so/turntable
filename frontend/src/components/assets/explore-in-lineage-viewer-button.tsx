"use client"
import { Asset } from "@/app/assets/page"
import { Button } from "@/components/ui/button"
import { SquareArrowOutUpRight } from "lucide-react"
import { useRouter } from "next/navigation"



export default function ExploreInLineageViewerButton({ asset }: { asset: Asset }) {

    const router = useRouter()
    return (
        <Button onClick={() => {
            router.push(`/lineage/${asset.id}`)
        }} className='gap-1 flex items-center' size='sm' variant='ghost'>
            <div>Open in Lineage Explorer</div>
            <SquareArrowOutUpRight className='w-4 h-4' />
        </Button>
    )
}