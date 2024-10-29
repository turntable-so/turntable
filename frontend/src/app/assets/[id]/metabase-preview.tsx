import { getMetabaseEmbedUrlForAsset } from "@/app/actions/actions";
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
    return (
      <Card className="rounded-md">
        <CardContent className="p-4">
          <div>
            <p className="text-sm">{result.detail}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return <iframe src={result.iframe_url} width="100%" height="600px" />;
}
