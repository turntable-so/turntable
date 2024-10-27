import {
  getMetabaseEmbedUrlForAsset,
  makeMetabaseAssetEmbeddable,
} from "@/app/actions/actions";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import AssetNotPublished from "./asset-not-published";

type MetabasePreviewProps = {
  asset: any;
};

export default async function MetabasePreview({ asset }: MetabasePreviewProps) {
  const result = await getMetabaseEmbedUrlForAsset(asset.id);

  if (result.detail === "NOT_EMBEDDED") {
    return <AssetNotPublished asset={asset} />;
  }

  if (result.detail) {
    return <div>{result.detail}</div>;
  }

  return (
    <iframe
      src={result.iframe_url}
      width="100%"
      height="600px"
      allowTransparency
    />
  );
}
