
"use client";
import { getAssetPreview, getAssets, getResources } from "@/app/actions/actions";
import { Asset } from "@/components/lineage/LineageView";
// contexts/GlobalContext.js
import React, { createContext, useContext, useEffect, useState } from "react";

import { v4 as uuidv4 } from "uuid";

// Create a context
const GlobalContext = createContext({});

// Export a custom hook to use the global context
export function useAppContext(): Context {
    return useContext(GlobalContext) as Context;
}

export type MenuTab = "Search" | "Notebooks" | "Sources" | "Models" | "Lineage";

export type Block = {
    id: string | undefined;
    type: "query" | "prompt";
    sql: string | undefined;
    title: string;
    records: any[];
    database: string;
};

type Notebook = {
    id: string | null;
    title: string;
    blocks: Block[];
};

type Context = {
    selectedMenuTab: MenuTab | null;
    setSelectedMenuTab: (tab: MenuTab) => void;
    setActiveNotebook: (notebook: Notebook) => void;
    sources: any[];
    addSource: (id: string) => void;
    activeNotebook: Notebook | null;
    assetPreview: any;
    fetchAssetPreview: (assetId: string) => void;
    clearAssetPreview: () => void;
    runQuery: (blockId: string) => void;
    onSqlChange: (blockId: string, sql: string) => void;
    toggleSidebar: (tab: MenuTab) => void;
    sidebarCollapsed: boolean;
    collapseSidebar: (collapse: boolean) => void;
    addPromptBlock: () => void;
    assets: any[];
    tags: string[];
    types: string[];
    areAssetsLoading: boolean;
    setIsLineageLoading: (loading: boolean) => void;
    isLineageLoading: boolean;
    setFocusedAsset: (asset: any) => void;
    focusedAsset: Asset | null;
    setAssetPreview: (asset: any) => void;
    insertCurrentSqlContent: { sql: string; title: string, resourceId: string } | null;
    setInsertCurrentSqlContent: ({
        sql,
        title,
        resourceId,
    }: {
        sql: string;
        title: string;
        resourceId: string;
    }) => void;
    resources: any[];
    fetchResources: () => void;
    setIsFullScreen: (isFullScreen: boolean) => void;
    isFullScreen: boolean;
    fullScreenData: any;
    setFullScreenData: (data: any) => void;
    notebookCharts: any;
    setNotebookCharts: (charts: any) => void;
    activeNode: any;
    setActiveNode: (data: any) => void;
};

export type AssetMap = {
    [resource_id: string]: {
        isLoading: boolean;
        assets: Asset[];
        name: string;
    };
};

export default function AppContextProvider({
    children,
}: {
    children: React.ReactElement;
}) {
    const [selectedMenuTab, setSelectedMenuTab] = useState<MenuTab | null>(
        "Notebooks"
    );
    const [assetPreview, setAssetPreview] = useState(null);


    const [assets, setAssets] = useState<AssetMap>({});
    const [tags, setTags] = useState<any[]>([]);
    const [types, setTypes] = useState([]);
    const [activeNotebook, setActiveNotebook] = useState<Notebook | null>(null);
    const [sidebarCollapsed, collapseSidebar] = useState(false);
    const [activeNode, setActiveNode] = useState(null);
    const [areAssetsLoading, setAreAssetsLoading] = useState<boolean>(false);
    const [isLineageLoading, setIsLineageLoading] = useState<boolean>(false);
    const [focusedAsset, setFocusedAsset] = useState<any>(null);
    const [insertCurrentSqlContent, setInsertCurrentSqlContent] = useState<
        object | null
    >(null);
    const [resources, setResources] = useState<any[]>([]);
    const [isFullScreen, setIsFullScreen] = useState<boolean>(false);
    const [fullScreenData, setFullScreenData] = useState<any>(false);

    const [notebookCharts, setNotebookCharts] = useState<any>({});

    const fetchResources = async () => {
        const data = await getResources();
        if (data) {
            setResources(data);
        }
    };

    useEffect(() => {
        fetchResources();
    }, []);


    const runQuery = async (blockId: string) => {
        if (!activeNotebook) {
            return;
        }

        const block = activeNotebook.blocks.find((b) => b.id === blockId);

        if (!block) {
            return;
        }
    };

    const onSqlChange = (blockId: string, sql: string) => {
        if (!activeNotebook) {
            return;
        }
        const block = activeNotebook.blocks.find((b) => b.id === blockId);

        if (!block) {
            return;
        }

        setActiveNotebook({
            ...activeNotebook,
            blocks: activeNotebook.blocks.map((b) => {
                if (b.id === blockId) {
                    return {
                        ...b,
                        sql,
                    };
                }
                return b;
            }),
        });
    };

    const fetchAssetPreview = async (assetId: string) => {
        const asset = await getAssetPreview(assetId);
        console.log({ asset });
        setAssetPreview(asset);
    };

    const addPromptBlock = () => {
        setActiveNotebook(
            // @ts-ignore
            {
                ...activeNotebook,
                blocks: [
                    // @ts-ignore
                    ...activeNotebook.blocks,
                    {
                        id: `block-${uuidv4()}`,
                        type: "prompt",
                        sql: "",
                        // @ts-ignore
                        title: `Query #${activeNotebook.blocks.length + 1}`,
                        records: [],
                        database: "",
                    },
                ],
            }
        );
    };

    const clearAssetPreview = () => {
        setAssetPreview(null);
        console.log("clearAssetPreview");
    };

    const value = {
        selectedMenuTab,
        setSelectedMenuTab,
        setActiveNotebook,
        activeNotebook,
        assetPreview,
        fetchAssetPreview,
        clearAssetPreview,
        runQuery,
        onSqlChange,
        sidebarCollapsed,
        collapseSidebar,
        addPromptBlock,
        assets,
        tags,
        types,
        areAssetsLoading,
        setIsLineageLoading,
        isLineageLoading,
        setFocusedAsset,
        focusedAsset,
        setAssetPreview,
        insertCurrentSqlContent,
        setInsertCurrentSqlContent,
        resources,
        fetchResources,
        setIsFullScreen,
        isFullScreen,
        fullScreenData,
        setFullScreenData,
        notebookCharts,
        setNotebookCharts,
        activeNode,
        setActiveNode,
    };

    return (
        <GlobalContext.Provider value={value}>{children}</GlobalContext.Provider>
    );
}