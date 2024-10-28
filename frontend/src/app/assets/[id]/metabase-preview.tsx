import { getMetabaseEmbedUrlForAsset } from "@/app/actions/actions";
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

  return <iframe src={result.iframe_url} width="100%" height="600px" />;
}
