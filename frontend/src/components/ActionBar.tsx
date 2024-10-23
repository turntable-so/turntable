"use client";
import { Button } from "@/components/ui/button";
import { useAppContext } from "@/contexts/AppContext";
import { Loader2, SlidersHorizontal } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Fragment, useEffect, useMemo, useRef, useState } from "react";
import useResizeObserver from "use-resize-observer";
import { getAssetIndex, getNotebooks } from "../app/actions/actions";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@radix-ui/react-dropdown-menu";
import { PopoverContent } from "@radix-ui/react-popover";
import ModelPreviewer from "./ModelPreviewer";
import { Card, CardContent } from "./ui/card";
import { Popover, PopoverTrigger } from "./ui/popover";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "./ui/resizable";

import { Tree } from "@/components/ui/tree";
import { cn, getAssetIcon, getLeafIcon } from "@/lib/utils";
import { Folder, Workflow } from "lucide-react";
import MultiSelect from "./ui/multi-select";
import { Asset } from "./ui/schema";
// @ts-ignore
const groupBy = (array, key) =>
  array.reduce((result: any, currentValue: any) => {
    (result[currentValue[key]] = result[currentValue[key]] || []).push(
      currentValue
    );
    return result;
  }, {});

type TreeDataNode = {
  id: string;
  name: string;
  icon?: any | null;
  children?: TreeDataNode[] | null;
  count?: number | null;
  isSelectable?: boolean;
  isLoading?: boolean;
};
const TreeDataNode = ({
  id,
  name,
  icon = null,
  children = null,
  isSelectable = false,
  isLoading = false,
  count = null,
}: TreeDataNode) => ({
  id,
  icon,
  name,
  isSelectable,
  isLoading,
  count,
  ...(children && { children }),
});


export const DbtLogo = () => (
  <svg
    width="16px"
    height="16px"
    viewBox="0 0 256 256"
    version="1.1"
    preserveAspectRatio="xMidYMid"
  >
    <g>
      <path
        d="M245.121138,10.6473813 C251.139129,16.4340053 255.074133,24.0723342 256,32.4050489 C256,35.8769778 255.074133,38.1917867 252.990862,42.5895822 C250.907876,46.9873778 225.215147,91.4286933 217.57696,103.696213 C213.179164,110.871609 210.864356,119.435947 210.864356,127.768462 C210.864356,136.3328 213.179164,144.6656 217.57696,151.840996 C225.215147,164.108516 250.907876,208.781084 252.990862,213.179164 C255.074133,217.57696 256,219.659947 256,223.131876 C255.074133,231.464676 251.370667,239.103147 245.352676,244.658347 C239.565938,250.676338 231.927751,254.611342 223.826489,255.305671 C220.35456,255.305671 218.039751,254.379804 213.873493,252.296533 C209.706951,250.213262 164.340053,225.215147 152.072249,217.57696 C151.146382,217.113884 150.220516,216.419556 149.063396,215.95648 L88.4195556,180.079502 C89.8082133,191.652693 94.9006222,202.763093 103.233138,210.864356 C104.853618,212.484551 106.473813,213.873493 108.325547,215.262151 C106.936604,215.95648 105.316409,216.651093 103.927751,217.57696 C91.6599467,225.215147 46.9873778,250.907876 42.5895822,252.990862 C38.1917867,255.074133 36.1085156,256 32.4050489,256 C24.0723342,255.074133 16.4340053,251.370667 10.8788338,245.352676 C4.86075733,239.565938 0.925858133,231.927751 0,223.594951 C0.231464676,220.123022 1.1573248,216.651093 3.00905244,213.641956 C5.09223822,209.24416 30.7848533,164.571307 38.42304,152.303787 C42.82112,145.128391 45.1356444,136.795591 45.1356444,128.231538 C45.1356444,119.6672 42.82112,111.3344 38.42304,104.159004 C30.7848533,91.4286933 4.86075733,46.75584 3.00905244,42.3580444 C1.1573248,39.3489067 0.231464676,35.8769778 0,32.4050489 C0.925858133,24.0723342 4.62930489,16.4340053 10.6473813,10.6473813 C16.4340053,4.62930489 24.0723342,0.925858133 32.4050489,0 C35.8769778,0.231464676 39.3489067,1.1573248 42.5895822,3.00905244 C46.2930489,4.62930489 78.9293511,23.6094009 96.28928,33.7939911 L100.224284,36.1085156 C101.612942,37.0343822 102.770347,37.7287111 103.696213,38.1917867 L105.547947,39.3489067 L167.348907,75.9204978 C165.960249,62.0324978 158.784853,49.3019022 147.674453,40.7378489 C149.063396,40.04352 150.683591,39.3489067 152.072249,38.42304 C164.340053,30.7848533 209.012622,4.86075733 213.410418,3.00905244 C216.419556,1.1573248 219.891484,0.231464676 223.594951,0 C231.696213,0.925858133 239.334684,4.62930489 245.121138,10.6473813 Z M131.240391,144.434062 L144.434062,131.240391 C146.285796,129.388658 146.285796,126.611342 144.434062,124.759609 L131.240391,111.565938 C129.388658,109.714204 126.611342,109.714204 124.759609,111.565938 L111.565938,124.759609 C109.714204,126.611342 109.714204,129.388658 111.565938,131.240391 L124.759609,144.434062 C126.379804,146.054258 129.388658,146.054258 131.240391,144.434062 Z"
        fill="#FF694A"
      ></path>
    </g>
  </svg>
);


type ResourceAsset = {
  id: string;
  name: string;
  subtype: string;
  has_dbt: boolean;
  assets: {
    id: string;
    name: string;
    type: string;
  }[];
}

export default function ActionBar({
  context,
}: {
  context: "NOTEBOOK" | "LINEAGE"
}) {
  const searchRef = useRef<HTMLInputElement>(null);
  const resizerRef = useRef<HTMLDivElement>(null);
  const { ref: treeRef, width, height } = useResizeObserver();

  const {
    // assets,
    clearAssetPreview,
    assetPreview,
    // areAssetsLoading,
    focusedAsset,
    setIsLineageLoading,
    tags,
    resources,
    types,
    fetchAssetPreview,
  } = useAppContext();
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isFilterPopoverOpen, setIsFilterPopoverOpen] = useState(false);
  const [treeData, setTreeData] = useState<any>([]);
  const [resourceAssets, setResourceAssets] = useState<ResourceAsset[]>([]);
  const [notebooks, setNotebooks] = useState<any>([]);
  type Item = Record<"value" | "label", string>;
  const [selectedTagFilters, setSelectedTagFilters] = useState<Item[]>([]);
  const [selectedTypeFilters, setSelectedTypeFilters] = useState<Item[]>([]);
  const [lowHeight, setLowheight] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const pathName = usePathname();
  const router = useRouter();
  const isNotebook = pathName.includes("/notebooks/");


  useEffect(() => {
    const fetchAssetIndex = async () => {
      setIsLoading(true);
      const data = await getAssetIndex();
      setIsLoading(false);
      setResourceAssets(data);
    }
    fetchAssetIndex();
  }, []);


  useEffect(() => {
    const fetchAndSetNotebooks = async () => {
      const data = await getNotebooks();
      setNotebooks(data);
    };
    fetchAndSetNotebooks();
  }, []);

  useEffect(() => {
    if (searchRef.current) {
      searchRef.current.focus();
    }
  }, [searchRef]);

  console.log({ resourceAssets })

  function createTreeDataNode(
    resource: any,
    assets: {
      id: string;
      name: string;
      type: string;
    }[],
    getAssetIcon: Function,
    groupBy: Function
  ) {
    if (assets.length === 0) {
      return TreeDataNode({
        icon: getAssetIcon("dbt", resource.subtype),
        id: resource.id,
        name: resource.name,
        isLoading: false,
        count: 0,
        children: [],
      });
    }

    const groupedAssets = groupBy(assets, "type");
    return TreeDataNode({
      icon: getAssetIcon("dbt", resource.subtype),
      id: resource.id,
      name: resource.name,
      count: Object.keys(groupedAssets).reduce(
        (acc, k) => acc + groupedAssets[k].length,
        0
      ),
      children: createChildrenNodes(
        resource,
        groupedAssets,
        getAssetIcon,
        groupBy
      ),
    });
  }

  function createChildrenNodes(
    resource: any,
    groupedAssets: any,
    getAssetIcon: Function,
    groupBy: Function
  ) {
    return Object.keys(groupedAssets).flatMap((k) => {
      if (resource.subtype.toLowerCase() === "looker") {
        return handleLookerResources(
          resource,
          k,
          groupedAssets[k],
          getAssetIcon,
          groupBy
        );
      } else {
        return createChildNode(resource, k, groupedAssets[k], getAssetIcon);
      }
    });
  }

  function handleLookerResources(
    resource: any,
    assetType: string,
    groupedAssets: any,
    getAssetIcon: Function,
    groupBy: Function
  ) {
    const nameGrouped = groupBy(groupedAssets, "type");
    return TreeDataNode({
      id: `${resource.id}-${assetType}`,
      name: `${assetType}s`, // Modified to show a grouped name if needed
      icon: getAssetIcon(assetType, resource.subtype),
      count: Object.keys(nameGrouped).length,
      children: Object.keys(nameGrouped)
        .sort((a, b) => a.localeCompare(b))
        .map((name) =>
          nameGrouped[name].length > 1
            ? createChildNode(
              resource,
              assetType,
              nameGrouped[name],
              getAssetIcon,
              name
            )
            : createFinalNode(nameGrouped[name][0], getLeafIcon(assetType))
        ),
    });
  }

  function createChildNode(
    resource: any,
    assetType: string,
    assets: Array<any>,
    getAssetIcon: Function,
    overrideName: string | null = null
  ) {
    return TreeDataNode({
      id: `${resource.id}-${assetType}-${overrideName || ""}`,
      name: `${overrideName || assetType}s`, // Modified to show a grouped name if needed
      icon: getAssetIcon(assetType, resource.subtype),
      count: assets.length,
      children: assets
        .sort((a, b) => a.name.localeCompare(b.name))
        .map((asset) => createFinalNode(asset, getLeafIcon(assetType))),
    });
  }

  function createFinalNode(asset: any, icon: any) {
    return TreeDataNode({
      id: asset.id,
      name: asset.name,
      isSelectable: true,
      icon: icon,
      count: 10,
    });
  }

  useEffect(() => {
    const treeData = resourceAssets.map((resource: ResourceAsset) => {
      return createTreeDataNode(
        resource,
        resource.assets.filter((asset: any) => asset.name.includes(searchQuery)),
        getAssetIcon,
        groupBy
      );
    });

    setTreeData(treeData);
  }, [resourceAssets, searchQuery]);
  const isCurrentNotebook = (pathName: string, id: string) => {
    return pathName.includes(id);
  };

  return (
    <div className="text-muted-foreground w-full h-fit flex flex-col">
      <div
        className={cn(
          "flex h-[52px] items-center justify-center",
          "h-[52px]"
        )}
      >
        <div className="flex space-x-2 w-full px-4">
          <input
            ref={searchRef}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="focus:outline-none bg-gray-100 w-full text-sm rounded-md py-2 px-2 border"
            placeholder="Filter assets"
          />
        </div>
        <div className="flex justify-between">
          {/* <div className="text-xs mt-2 px-1 invisible">
            {filteredAssets.length} Assets
          </div> */}
          {selectedTagFilters.length + selectedTypeFilters.length > 0 && (
            <div className="text-xs mt-2 px-1 bg-gray-100">
              {selectedTagFilters.length + selectedTypeFilters.length} Filters
            </div>
          )}
        </div>
      </div>
      <div
        className={`flex-grow border-t mt-0 h-500 ${isFilterPopoverOpen ? "z-[-1]" : ""
          }`}
      >
        <Tabs defaultValue="assets" className="h-full">
          <TabsList
            className="grid w-full h-100 grid-cols-2"
            style={
              !isNotebook
                ? {
                  opacity: 0,
                  pointerEvents: "none",
                  height: 0,
                }
                : {}
            }
          >
            <TabsTrigger
              value="assets"
              style={
                !isNotebook
                  ? {
                    opacity: 0,
                    pointerEvents: "none",
                  }
                  : {}
              }
            >
              Assets
            </TabsTrigger>
            {isNotebook && <TabsTrigger value="pages">Pages</TabsTrigger>}
          </TabsList>
          <TabsContent value="assets" style={{ height: "100%" }}>
            <div className="h-full">
              {!assetPreview ? (
                <div className="flex flex-col h-full max-h-screen z-0">
                  {isLoading ? (
                    <div className="flex items-center justify-center h-full">
                      <Loader2 className="h-6 w-6 animate-spin opacity-50" />
                    </div>
                  ) : (
                    <Fragment>
                      <div ref={treeRef} className="flex flex-col h-full">
                        <Tree
                          height={"100%"}
                          width={width}
                          data={treeData}
                          initialSlelectedItemId="f12"
                          onSelectChange={(item) => {
                            if (item?.isSelectable) {
                              if (context === "LINEAGE") {
                                if (focusedAsset?.id !== item.id) {
                                  setIsLineageLoading(true);
                                  router.push(`/lineage/${item.id}`);
                                }
                              } else {
                                fetchAssetPreview(item.id);
                              }
                            }
                          }}
                          folderIcon={Folder}
                          itemIcon={Workflow}
                        />
                      </div>
                    </Fragment>
                  )}
                </div>
              ) : (
                <ResizablePanelGroup
                  direction="vertical"
                  className="z-0"
                  style={{ height: "100%" }}
                >
                  <ResizablePanel defaultSize={25}>
                    {isLoading ? (
                      <div className="flex items-center justify-center h-full">
                        <Loader2 className="h-6 w-6 animate-spin opacity-50" />
                      </div>
                    ) : (
                      <Fragment>
                        <div ref={treeRef} className="flex flex-col h-full">
                          <Tree
                            height={height}
                            width={width}
                            data={treeData}
                            initialSlelectedItemId="f12"
                            onSelectChange={(item) => {
                              if (item?.isSelectable) {
                                if (context === "LINEAGE") {
                                  if (focusedAsset?.id !== item.id) {
                                    setIsLineageLoading(true);
                                    router.push(`/lineage/${item.id}`);
                                  }
                                } else {
                                  fetchAssetPreview(item.id);
                                }
                              }
                            }}
                            folderIcon={Folder}
                            itemIcon={Workflow}
                          />
                        </div>
                        <div className="h-[150x]" />
                      </Fragment>
                    )}
                  </ResizablePanel>
                  <ResizableHandle withHandle className="bg-gray-300" />
                  <ResizablePanel
                    defaultSize={75}
                    className="p-0"
                    onResize={(
                      e: number | undefined,
                      size: number | undefined
                    ) => {
                      setLowheight(
                        ((size as number) / 100.0) * window.innerHeight
                      );
                    }}
                  >
                    <ModelPreviewer
                      context={context}
                      clearAsset={clearAssetPreview}
                      asset={assetPreview}
                    />
                  </ResizablePanel>
                </ResizablePanelGroup>
              )}
            </div>
          </TabsContent>
          {isNotebook && (
            <TabsContent value="pages">
              {(notebooks || []).map((notebook: any) => (
                <div className="w-full" key={notebook.title}>
                  <Button
                    variant={"ghost"}
                    size="icon"
                    className={`w-full ${isCurrentNotebook(pathName, notebook.id)
                      ? "opacity-100"
                      : "opacity-50"
                      } ${isCurrentNotebook(pathName, notebook.id)
                        ? "bg-"
                        : "bg-transparent"
                      } `}
                    aria-label={notebook.title}
                  >
                    <Link href={`/notebooks/${notebook.id}`} className="w-full">
                      <div
                        className={`${isCurrentNotebook(pathName, notebook.id)
                          ? "bg-[#ebebeb]"
                          : "hover:bg-[#ebebeb]"
                          } px-4 p-2 w-full flex  space-x-2`}
                      >
                        <p className="font-normal text-[15px]">
                          {notebook.title}
                        </p>
                      </div>
                    </Link>
                  </Button>
                </div>
              ))}
            </TabsContent>
          )}
        </Tabs>
      </div>
    </div>
  );
}
