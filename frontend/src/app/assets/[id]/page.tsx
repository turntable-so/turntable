import { getAssetPreview } from "@/app/actions/actions";
import { Card, CardContent } from "@/components/ui/card";

import ExploreInLineageViewerButton from "@/components/assets/explore-in-lineage-viewer-button";
import LineagePreview from "@/components/lineage/LineagePreview";
import { Badge } from "@/components/ui/badge";
import { getResourceIcon } from "@/lib/utils";
import ColumnsTable from "./columns-table";
import MetabasePreview from "./metabase-preview";

type AssetPageProps = {
  params: { id: string };
};

export default async function AssetPage({ params }: AssetPageProps) {
  const asset = await getAssetPreview(params.id);

  const validMetabaseSubtypes = ["chart", "dashboard"];
  const showMetabasePreview =
    asset.resource_type === "metabase" &&
    validMetabaseSubtypes.includes(asset.type);

  const showSchema =
    asset.schema || asset.dataset || asset.table_name || asset.tags?.length;

  return (
    <div className="w-full h-screen flex justify-center pb-16">
      <div className="max-w-7xl w-full px-16 pt-16 overflow-y-auto hide-scrollbar">
        <div className="flex gap-4 items-center">
          <div className="mb-8">
            <h1 className="text-2xl font-medium text-black dark:text-white">
              {asset.name}
            </h1>
            <div className="flex gap-6 my-2 items-center">
              <div>
                <div className="flex gap-2 items-center">
                  <div>{getResourceIcon(asset.resource_subtype)}</div>
                  <div>{asset.resource_has_dbt && getResourceIcon("dbt")}</div>
                  <div className="text-sm text-gray-500 dark:text-gray-300">
                    {asset.unique_name}
                  </div>
                </div>
              </div>
              <Badge variant="outline">{asset.type?.toUpperCase()}</Badge>
            </div>
          </div>
        </div>
        <div className="flex flex-col gap-8 w-full pb-12">
          {showSchema ? (
            <div>
              <div className="font-medium text-muted-foreground my-1 text-lg">
                Details
              </div>
              <Card className="rounded-md">
                <CardContent className="p-4">
                  <div className="flex gap-6">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-300">
                        Schema
                      </p>
                      <p className="text-sm my-1">{asset.schema}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-300">
                        Dataset
                      </p>
                      <p className="text-sm my-1">{asset.dataset}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-300">
                        Table
                      </p>
                      <p className="text-sm my-1">{asset.table_name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-300">
                        Tags
                      </p>
                      <div className="flex gap-2 my-1">
                        {asset.tags ? (
                          <p className="text-sm text-gray-500 dark:text-gray-300">
                            {asset.tags.map((tag: string) => (
                              <Badge variant="secondary" key={tag}>
                                {tag}
                              </Badge>
                            ))}
                          </p>
                        ) : (
                          <p className="text-sm text-gray-500 dark:text-gray-300 italic">
                            No tags
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : null}
          {asset.description ? (
            <div>
              <div className="font-medium text-muted-foreground my-1 text-lg">
                Summary
              </div>
              <Card className="rounded-md">
                <CardContent className="p-4">
                  <div>
                    <p className="text-sm">{asset.description}</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : null}
          {asset.columns?.length ? (
            <div>
              <div className="font-medium text-muted-foreground my-1  text-lg">
                Columns
              </div>
              <Card className="rounded-md">
                <ColumnsTable columns={asset.columns} />
              </Card>
            </div>
          ) : null}
          {showMetabasePreview && (
            <div>
              <div className="font-medium text-muted-foreground my-1  text-lg">
                Preview
              </div>
              <MetabasePreview asset={asset} />
            </div>
          )}
          <div>
            <div className="flex justify-between items-center">
              <div className="font-medium text-muted-foreground my-1 text-lg">
                Lineage
              </div>
              <ExploreInLineageViewerButton asset={asset} />
            </div>
            <Card className="rounded-md h-[600px] ">
              <LineagePreview nodeId={params.id} />
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
