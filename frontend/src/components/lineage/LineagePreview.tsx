"use client";

import { getLineage } from "@/app/actions/actions";
import LineageView from "@/components/lineage/LineagePreview";
import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { ErrorBoundary } from "react-error-boundary";

export default function LineagePreview({ nodeId }: { nodeId: string }) {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [lineage, setLineage] = useState<any>(null);
  const [rootAsset, setRootAsset] = useState<any>(null);

  useEffect(() => {
    const fetchLineage = async () => {
      setIsLoading(true);
      try {
        const { lineage, root_asset } = await getLineage({
          nodeId,
          successor_depth: 1,
          predecessor_depth: 1,
          lineage_type: "all",
        });
        setLineage(lineage);
        setRootAsset(root_asset);
      } catch (error) {
        console.error("Error fetching lineage:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLineage();
  }, []);

  return (
    <div>
      <ErrorBoundary FallbackComponent={() => <div>Something went wrong</div>}>
        {isLoading ? (
          <div className="h-[400px] flex items-center justify-center text-gray-300">
            <Loader2 className="h-6 w-6 animate-spin" />
          </div>
        ) : (
          lineage &&
          rootAsset && (
            <LineageView
              lineage={lineage}
              rootAsset={rootAsset}
              style={{ height: "600px" }}
              page={"lineage"}
            />
          )
        )}
      </ErrorBoundary>
    </div>
  );
}
