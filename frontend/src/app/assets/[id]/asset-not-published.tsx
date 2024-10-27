"use client";

import { makeMetabaseAssetEmbeddable } from "@/app/actions/actions";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";

type AssetNotPublishedProps = {
  asset: any;
};

export default function AssetNotPublished({ asset }: AssetNotPublishedProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [text, setText] = useState(
    "This asset is not published. Click the button to the right to publish and embed.",
  );
  const [isFetching, setIsFetching] = useState(false);
  const isMutating = isFetching || isPending;

  const handleEmbed = async () => {
    const result = await makeMetabaseAssetEmbeddable(asset.id);
    if (result.detail === "ASSET_EMBEDDED") {
      startTransition(() => {
        router.refresh();
      });
    } else if (result.detail) {
      setText(result.detail);
    } else {
      setText("An error occurred while embedding the asset.");
    }
  };

  return (
    <Card className="rounded-md">
      <CardContent className="p-4 flex flex-row justify-between items-center gap-4">
        <p>{text}</p>
        <Button onClick={handleEmbed} disabled={isMutating}>
          {isMutating ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            "Embed Asset"
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
