import { makeMetabaseAssetEmbeddable } from "@/app/actions/actions";
import { useFiles } from "@/app/contexts/FilesContext";
import { Loader2 } from "lucide-react";
import { useState } from "react";
import { Button } from "../ui/button";

type EmbedAssetProps = {
  assetId: string;
  onEmbedded: () => void; // Add the callback prop
};

export default function EmbedAsset({ assetId, onEmbedded }: EmbedAssetProps) {
  const { setActiveFile } = useFiles();
  const [text, setText] = useState(
    "This asset is not published. Click the button to the right to publish and embed.",
  );
  const [isFetching, setIsFetching] = useState(false);

  const handleEmbed = async () => {
    setIsFetching(true);
    const result = await makeMetabaseAssetEmbeddable(assetId);
    if (result.detail === "ASSET_EMBEDDED") {
      // Call the callback function
      onEmbedded();
    } else if (result.detail) {
      setText(result.detail);
    } else {
      setText("An error occurred while embedding the asset.");
    }
    setIsFetching(false);
  };

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <p>{text}</p>
      <Button onClick={handleEmbed} disabled={isFetching}>
        {isFetching ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          "Embed Asset"
        )}
      </Button>
    </div>
  );
}
