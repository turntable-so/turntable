"use client";
import { useAppContext } from "@/contexts/AppContext";
import useResizeObserver from "use-resize-observer";
import { Button } from "@/components/ui/button";
import { Loader2, SlidersHorizontal } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { Fragment, memo, useEffect, useMemo, useRef, useState } from "react";
import { FixedSizeList as List } from "react-window";
import { getNotebooks } from "../app/actions/actions";
import Link from 'next/link'

import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "./ui/resizable";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"
import ModelPreviewer from "./ModelPreviewer";
import { Popover, PopoverTrigger } from "./ui/popover";
import { PopoverContent } from "@radix-ui/react-popover";
import { Card, CardContent } from "./ui/card";
import { Label } from "@radix-ui/react-dropdown-menu";

import { FancyMultiSelect } from "./ui/multi-select";
import { getAssetIcon, getLeafIcon } from "@/lib/utils";
import { ScrollArea } from "./ui/scroll-area";
import { Tree } from "@/components/ui/tree";
import { Workflow, Folder, Layout } from "lucide-react";
import { Asset } from "./lineage/LineageView";
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

const BigQueryLogo = () => (
  <svg
    height="16px"
    width="16px"
    xmlns="http://www.w3.org/2000/svg"
    viewBox="-1.633235433328256 7.0326093303156565 131.26574682416876 114.63439066968435"
  >
    <linearGradient
      id="a"
      gradientUnits="userSpaceOnUse"
      x1="64"
      x2="64"
      y1="7.034"
      y2="120.789"
    >
      <stop offset="0" stop-color="#4387fd" />
      <stop offset="1" stop-color="#4683ea" />
    </linearGradient>
    <path
      d="M27.79 115.217L1.54 69.749a11.499 11.499 0 0 1 0-11.499l26.25-45.467a11.5 11.5 0 0 1 9.96-5.75h52.5a11.5 11.5 0 0 1 9.959 5.75l26.25 45.467a11.499 11.499 0 0 1 0 11.5l-26.25 45.467a11.5 11.5 0 0 1-9.959 5.749h-52.5a11.499 11.499 0 0 1-9.96-5.75z"
      fill="url(#a)"
    />
    <path
      clip-path="url(#b)"
      d="M119.229 86.48L80.625 47.874 64 43.425l-14.933 5.55L43.3 64l4.637 16.729 40.938 40.938 8.687-.386z"
      opacity=".07"
    />
    <g fill="#fff">
      <path d="M64 40.804c-12.81 0-23.195 10.385-23.195 23.196 0 12.81 10.385 23.195 23.195 23.195S87.194 76.81 87.194 64c0-12.811-10.385-23.196-23.194-23.196m0 40.795c-9.72 0-17.6-7.88-17.6-17.6S54.28 46.4 64 46.4 81.6 54.28 81.6 64 73.72 81.6 64 81.6" />
      <path d="M52.99 63.104v7.21a12.794 12.794 0 0 0 4.38 4.475V63.104zM61.675 57.026v19.411c.745.137 1.507.22 2.29.22.714 0 1.41-.075 2.093-.189V57.026zM70.766 66.1v8.562a12.786 12.786 0 0 0 4.382-4.7v-3.861zM80.691 78.287l-2.403 2.405a1.088 1.088 0 0 0 0 1.537l9.115 9.112a1.088 1.088 0 0 0 1.537 0l2.403-2.402a1.092 1.092 0 0 0 0-1.536l-9.116-9.116a1.09 1.09 0 0 0-1.536 0" />
    </g>
  </svg>
);

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

type Model = {
  id: string;
  name: string;
  tags: string[];
  type: string;
};

export default function ActionBar({
  context,
}: {
  context: "NOTEBOOK" | "LINEAGE";
}) {
  const searchRef = useRef<HTMLInputElement>(null);
  const resizerRef = useRef<HTMLDivElement>(null);
  const { ref: treeRef, width, height } = useResizeObserver();

  const {
    assets,
    clearAssetPreview,
    assetPreview,
    areAssetsLoading,
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
  const [notebooks, setNotebooks] = useState<any>([]);
  type Item = Record<"value" | "label", string>;
  const [selectedTagFilters, setSelectedTagFilters] = useState<Item[]>([]);
  const [selectedTypeFilters, setSelectedTypeFilters] = useState<Item[]>([]);
  const [lowHeight, setLowheight] = useState<number>(0);
  const pathName = usePathname();
  const router = useRouter();
  const isNotebook = pathName.includes('/notebooks/');

  const filteredAssets = useMemo(() => {
    if (!assets) return {};

    return Object.entries(assets).reduce((acc, [resourceId, entry]) => {
      const filteredAssetsFromQuery = entry.assets.filter((asset: Model) =>
        asset.name.toLowerCase().includes(searchQuery.toLowerCase())
      );

      const filteredAssetsFromTags =
        selectedTagFilters.length > 0
          ? filteredAssetsFromQuery.filter((asset: Model) =>
            selectedTagFilters.some(
              (tag) => asset.tags && asset.tags.includes(tag.value)
            )
          )
          : filteredAssetsFromQuery;

      acc[resourceId] = {
        ...entry,
        assets: filteredAssetsFromTags,
      };

      return acc;
    }, {} as Record<string, (typeof assets)[keyof typeof assets]>);
  }, [assets, searchQuery, selectedTagFilters]);

  useEffect(() => {
    const fetchAndSetNotebooks = async () => {
      const data = await getNotebooks();
      setNotebooks(data);
    }
    fetchAndSetNotebooks();
  }, [])
  
  useEffect(() => {
    if (searchRef.current) {
      searchRef.current.focus();
    }
  }, [searchRef]);

  function createTreeDataNode(
    resource: any,
    assetsForResource: any,
    getAssetIcon: Function,
    groupBy: Function
  ) {
    if (assetsForResource.assets.length === 0) {
      return TreeDataNode({
        icon: getAssetIcon("dbt", resource.type),
        id: resource.id,
        name: resource.name,
        isLoading: assetsForResource.isLoading,
        count: 0,
        children: [],
      });
    }

    const groupedAssets = groupBy(assetsForResource.assets, "type");

    return TreeDataNode({
      icon: getAssetIcon("dbt", resource.type),
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

  function createChildrenNodes(resource: any, groupedAssets: any, getAssetIcon: Function, groupBy: Function) {
    return Object.keys(groupedAssets).flatMap((k) => {
      if (resource.name.toLowerCase() === "looker") {
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
    const nameGrouped = groupBy(groupedAssets, "name");
    return TreeDataNode({
      id: `${resource.id}-${assetType}`,
      name: `${assetType}s`, // Modified to show a grouped name if needed
      icon: getAssetIcon(assetType, resource.type),
      count: Object.keys(nameGrouped).length,
      children: Object.keys(nameGrouped).sort((a, b) => a.localeCompare(b)).map((name) =>
        nameGrouped[name].length > 1
          ? createChildNode(
            resource,
            assetType,
            nameGrouped[name],
            getAssetIcon,
            name
          )
          : createFinalNode(
            nameGrouped[name][0],
            getLeafIcon(assetType)
          )
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
      icon: getAssetIcon(assetType, resource.type),
      count: assets.length,
      children: assets.sort((a, b) => a.name.localeCompare(b.name)).map((asset) =>
        createFinalNode(asset, getLeafIcon(assetType))
      ),
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
    const treeData = resources.map((resource) => {
      const assetsForResource = filteredAssets[resource.id] || { assets: [] };
      return createTreeDataNode(
        resource,
        assetsForResource,
        getAssetIcon,
        groupBy
      );
    });

    setTreeData(treeData);
  }, [filteredAssets, resources]);
  const isCurrentNotebook = (pathName, id) => {
    return pathName.includes(id);
  }
  
  return (
    <div className="text-muted-foreground w-full mt-1 h-screen flex flex-col">
      <div className="sticky top-0 p-2 pt-4">
        <div className="flex space-x-2">
          <input
            ref={searchRef}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="focus:outline-none bg-gray-100 w-full text-sm rounded-md py-1 px-2 border"
            placeholder="Filter assets"
          />
          <Popover onOpenChange={(isOpen) => setIsFilterPopoverOpen(isOpen)}>
            <PopoverTrigger asChild>
              <Button
                variant="secondary"
                className="hover:border-black hover:opacity-80 py-0 px-2 border"
              >
                <SlidersHorizontal size="14" />
              </Button>
            </PopoverTrigger>
            <PopoverContent align="end" className=" mt-2 mr-2 ">
              <Card className="w-[300px]">
                <CardContent>
                  <form>
                    <input
                      style={{
                        position: "absolute",
                        opacity: 0,
                        height: 0,
                        width: 0,
                        border: "none",
                      }}
                    />
                    <div className="grid w-full items-center  text-muted-foreground space-y-4 mt-4">
                      <Label className="flex space-x-1 items-center">
                        <div className="text-sm pl-1">Filter by tag</div>
                      </Label>
                      <FancyMultiSelect
                        items={tags.map((tag: string) => ({
                          label: tag,
                          value: tag,
                        }))}
                        selected={selectedTagFilters}
                        setSelected={setSelectedTagFilters}
                        label="Select tags"
                      />
                    </div>
                    {/*<div className="grid w-full items-center  text-muted-foreground space-y-4 mt-4">
                      <Label className="flex space-x-1 items-center">
                        <div className="text-sm pl-1">Filter by asset type</div>
                      </Label>
                      <FancyMultiSelect
                        items={types.map((type: string) => ({
                          label: type,
                          value: type,
                        }))}
                        selected={selectedTypeFilters}
                        setSelected={setSelectedTypeFilters}
                        label="Select asset type"
                      />
                    </div>*/}
                  </form>
                </CardContent>
              </Card>
            </PopoverContent>
          </Popover>
        </div>
        <div className="flex justify-between">
          <div className="text-xs mt-2 px-1 invisible">
            {filteredAssets.length} Assets
          </div>
          {selectedTagFilters.length + selectedTypeFilters.length > 0 && (
            <div className="text-xs mt-2 px-1 bg-gray-100">
              {selectedTagFilters.length + selectedTypeFilters.length} Filters
            </div>
          )}
        </div>
      </div>
      <div
        className={`flex-grow border-t mt-0 ${isFilterPopoverOpen ? "z-[-1]" : ""
          }`}
      >
        <Tabs defaultValue="assets">
          <TabsList className="grid w-full grid-cols-2" style={!isNotebook ? {
              opacity: 0,
              pointerEvents: "none",
              height: 0
            } : {}}>
            <TabsTrigger value="assets" style={!isNotebook ? {
              opacity: 0,
              pointerEvents: "none"
            } : {}}>Assets</TabsTrigger>
            {isNotebook && <TabsTrigger value="pages">Pages</TabsTrigger>}
          </TabsList>
          <TabsContent value="assets">
          {!assetPreview ? (
          <div className="flex flex-col h-full max-h-screen z-0">
            {false ? (
              <div className="flex items-center justify-center h-full">
                <Loader2 className="mr-2 h-8 w-8 animate-spin opacity-50" />
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
          </div>
        ) : (
          <ResizablePanelGroup direction="vertical" className="z-0">
            <ResizablePanel defaultSize={25}>
              {areAssetsLoading ? (
                <div className="flex items-center justify-center h-full">
                  <Loader2 className="mr-2 h-8 w-8 animate-spin opacity-50" />
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
              onResize={(e: number | undefined, size: number | undefined) => {
                setLowheight(((size as number) / 100.0) * window.innerHeight);
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
          </TabsContent>
          <TabsContent value="pages">
              {
                (notebooks || []).map((notebook:any) => (
                  <div className='w-full'
                  key={notebook.title}>
                  <Button

                      variant={'ghost'}
                      size="icon"
                      className={`w-full ${isCurrentNotebook(pathName, notebook.id) ? 'opacity-100' : 'opacity-50'} ${isCurrentNotebook(pathName, notebook.id) ? 'bg-' : 'bg-transparent'} `}
                      aria-label={notebook.title}
                  >
                      <Link href={`/notebooks/${notebook.id}`} className="w-full">
                          <div className={`${isCurrentNotebook(pathName, notebook.id) ? 'bg-[#ebebeb]' : 'hover:bg-[#ebebeb]'} px-4 p-2 w-full flex  space-x-2`}>
                              <p className="font-normal text-[15px]">{notebook.title}</p>
                          </div>
                      </Link>
                  </Button>
              </div>
                ))
              }

          </TabsContent>
        </Tabs>
        
      </div>
    </div>
  );
}
