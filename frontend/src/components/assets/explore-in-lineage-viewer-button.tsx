"use client";
import { Button } from "@/components/ui/button";
import type { Asset } from "@/components/ui/schema";
import { Loader2, SquareArrowOutUpRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function ExploreInLineageViewerButton({
  asset,
}: { asset: Asset }) {
  const [isNavigating, setIsNavigating] = useState<boolean>(false);

  const router = useRouter();
  return (
    <Button
      onClick={() => {
        setIsNavigating(true);
        router.push(`/lineage/${asset.id}`);
      }}
      className={`${isNavigating ? "opacity-50" : ""} gap-1 flex items-center opacity`}
      size="sm"
      variant="ghost"
    >
      <div>Open in Lineage Explorer</div>
      {isNavigating ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : (
        <SquareArrowOutUpRight className="w-4 h-4" />
      )}
    </Button>
  );
}
