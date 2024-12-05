"use client";

import { type Edge, ReactFlowProvider } from "@xyflow/react";
import { AlertCircle } from "lucide-react";
import { useParams, usePathname } from "next/navigation";
import React, { useEffect, useRef, useState } from "react";
import { ErrorBoundary } from "react-error-boundary";
import ColumnLineage from "../../components/lineage/ColumnLineage";
import { Alert, AlertDescription, AlertTitle } from "../../components/ui/alert";
import { useAppContext } from "../../contexts/AppContext";
import { getLineage, getProjectBasedLineage } from "../actions/actions";
import { useFiles } from "./FilesContext";

export type WithMousePosition<T> = T & {
  mousePosition: {
    x: number;
    y: number;
  };
};

export type ColumnWithPosition = WithMousePosition<{
  columnId: string;
}>;

export type LineageOptions = {
  lineageType: "all" | "direct_only";
  predecessor_depth: number;
  successor_depth: number;
  asset_only: boolean;
};

export type Lineage = {
  asset_id: string;
  assets: Asset[];
  asset_links: {
    id: string;
    source: string;
    target: string;
  };
  column_links: {
    id: string;
    source: string;
    target: string;
  };
};

export const LineageViewContext = React.createContext<{
  lineage: any | null;
  isTableOnly: boolean;
  isLoading: boolean;
  isLoadingColumns: boolean;
  isFilterOpen: boolean;
  isLineageLevelSelectorOpen: boolean;
  toggleFilter: () => void;
  error: string | null;
  selectedColumn: string | null;
  hoveredColumn: ColumnWithPosition | null;
  expandedNodes: string[];
  hoveredNode: {
    nodeId: string;
    yPos: number;
  } | null;
  hoveredEdge: WithMousePosition<Edge> | null;
  selectedEdge: WithMousePosition<Edge> | null;
  reactFlowWrapper: React.RefObject<HTMLDivElement> | null;
  modelsMap: Record<string, any>;
  handleSelectColumn: (columnId: string) => void;
  handleExpandNode: (nodeId: string) => void;
  handleColumnHover: (column: ColumnWithPosition | null) => void;
  onTableHeaderClick: (nodeId: string, filePath: string) => Promise<void>;
  onMouseEnterNode: (nodeId: string, yPos: number) => void;
  onMouseLeaveNode: () => void;
  updateHoveredEdge: (edge: WithMousePosition<Edge> | null) => void;
  updateSelectedEdge: (edge: WithMousePosition<Edge> | null) => void;
  isLineageOptionsPanelOpen: boolean;
  setIsLineageOptionsPanelOpen: React.Dispatch<React.SetStateAction<boolean>>;
  updateGraph: (options: LineageOptions, showLoading?: boolean) => void;
  rootAsset: Asset | null;
  lineageOptions: LineageOptions;
  setIsLineageLevelSelectorOpen: (open: boolean) => void;
  setLineageOptionsAndRefetch: (
    options: LineageOptions,
    { shouldCheckLineageData }?: { shouldCheckLineageData?: boolean },
  ) => void;
}>({
  lineage: null,
  isTableOnly: true,
  isFilterOpen: false,
  toggleFilter: () => {},
  isLoading: true,
  isLoadingColumns: true,
  error: null,
  hoveredEdge: null,
  selectedEdge: null,
  selectedColumn: null,
  hoveredColumn: null,
  expandedNodes: [],
  hoveredNode: null,
  reactFlowWrapper: null,
  modelsMap: {},
  lineageOptions: {
    predecessor_depth: 1,
    successor_depth: 1,
    lineageType: "all",
    asset_only: true,
  },
  isLineageOptionsPanelOpen: false,
  setIsLineageOptionsPanelOpen: () => {},
  handleSelectColumn: () => {},
  handleExpandNode: () => {},
  handleColumnHover: () => {},
  onTableHeaderClick: () => Promise.resolve(),
  onMouseEnterNode: () => {},
  onMouseLeaveNode: () => {},
  updateHoveredEdge: () => {},
  updateSelectedEdge: () => {},
  updateGraph: () => {},
  rootAsset: null,
  isLineageLevelSelectorOpen: false,
  setIsLineageLevelSelectorOpen: () => {},
  setLineageOptionsAndRefetch: () => {},
});

type Column = {
  id: string;
  type: string;
  name: string;
  description: string | null;
};

export type Asset = {
  id: string;
  type: "source" | "model";
  created_at: string;
  updated_at: string;
  description: string;
  unique_name: string;
  config: any;
  repository_id: string;
  read_only: boolean;
  columns: Column[];
  name: string;
};

type LineageViewProviderProps = {
  children: React.ReactNode;
};

type LineageFetchType =
  | {
      type: "asset";
      data: {
        nodeId: string;
      };
    }
  | {
      type: "project";
      data: {
        branchId: string;
        filePath: string;
      };
    };

export function LineageViewProvider({ children }: LineageViewProviderProps) {
  const { setFocusedAsset, setAssetPreview } = useAppContext();
  const { lineageData, setLineageData, branchId, activeFile } = useFiles();
  const pathname = usePathname();
  const params = useParams<{ id: string }>();

  const isAssetLineage = !!(
    (pathname.includes("lineage") || pathname.includes("asset")) &&
    params.id
  );
  const isProjectLineage = pathname.includes("editor");

  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingColumns, setIsLoadingColumns] = useState(false);
  const [isTableOnly, setIsTableOnly] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lineage, setLineage] = useState<Lineage | null>(null);
  const [rootAsset, setRootAsset] = useState<Asset | null>(null);
  const [isLineageOptionsPanelOpen, setIsLineageOptionsPanelOpen] =
    useState(false);
  const [lineageOptions, setLineageOptions] = useState<LineageOptions>({
    predecessor_depth: 1,
    successor_depth: 1,
    lineageType: "all",
    asset_only: true,
  });
  const [modelsMap, setModelsMap] = useState<Record<string, any>>({});
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [isLineageLevelSelectorOpen, setIsLineageLevelSelectorOpen] =
    useState(false);
  const [hoveredEdge, setHoveredEdge] =
    useState<WithMousePosition<Edge> | null>(null);
  const [selectedEdge, setSelectedEdge] =
    useState<WithMousePosition<Edge> | null>(null);
  const [selectedColumn, setSelectedColumn] = useState<string | null>(null);
  const [hoveredColumn, setHoveredColumn] = useState<ColumnWithPosition | null>(
    null,
  );
  const [expandedNodes, setExpandedNodes] = useState<string[]>([]);
  const [hoveredNode, setHoveredNode] = useState<{
    nodeId: string;
    yPos: number;
  } | null>(null);
  const [lineageFetchType, setLineageFetchType] =
    useState<LineageFetchType | null>(null);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

  const toggleFilter = () => {
    setIsFilterOpen((prev) => !prev);
  };

  const resetSelections = () => {
    setSelectedColumn(null);
    setSelectedEdge(null);
    setExpandedNodes([]);
    setHoveredNode(null);
    setHoveredEdge(null);
    setHoveredColumn(null);
  };

  const updateGraph = (options: LineageOptions, showLoading = true) => {
    if (options.predecessor_depth < 0 || options.successor_depth < 0) {
      console.warn("Invalid lineage options", options);
      return;
    }

    setLineageOptions(options);

    if (showLoading) {
      resetSelections();
      setIsLoading(true);
    }
  };

  async function getColumnLineage() {
    // setIsLoadingColumns(true);
    // // const data = request()
    // if ((data?.lineage?.links || []).length > 1) {
    //     console.log('webview.lineage.columns.success');
    // }
    // setIsLoadingColumns(false);
  }

  const updateHoveredEdge = (edge: WithMousePosition<Edge> | null) => {
    setHoveredEdge(edge);
  };

  const updateSelectedEdge = (edge: WithMousePosition<Edge> | null) => {
    if (edge != null && selectedEdge != null && edge.id === selectedEdge.id) {
      setSelectedEdge(null);
    } else {
      setSelectedEdge(edge);
    }
  };

  const handleSelectColumn = (columnId: string) => {
    // this allows for a toggle experience
    if (selectedColumn === columnId) {
      setSelectedColumn(null);
    } else {
      setSelectedColumn(columnId);
    }

    setSelectedEdge(null);
  };

  const handleColumnHover = (column: ColumnWithPosition | null) => {
    if (column != null && column.columnId === selectedColumn) {
      // don't show hover state if column is selected
      // this prevents the weird double click required to deselect
      return;
    }

    setHoveredColumn(column);
  };

  const handleExpandNode = (nodeId: string) => {
    if (expandedNodes.includes(nodeId)) {
      setExpandedNodes(expandedNodes.filter((id) => id !== nodeId));
      return;
    }

    setExpandedNodes([...expandedNodes, nodeId]);
  };

  const onTableHeaderClick = async (nodeId: string, filePath: string) => {
    // request('OPEN_FILE', { nodeId, filePath });
  };

  const onMouseEnterNode = (nodeId: string, yPos: number) => {
    setHoveredNode({
      nodeId,
      yPos,
    });
  };

  const onMouseLeaveNode = () => {
    setHoveredNode(null);
  };

  const setLineageOptionsAndRefetch = async (
    options: LineageOptions,
    {
      shouldCheckLineageData = true,
    }: { shouldCheckLineageData?: boolean } = {},
  ) => {
    setLineageOptions((prev) => ({
      ...prev,
      ...options,
    }));
    resetSelections();

    if (lineageFetchType?.type === "asset") {
      const data = await getLineage({
        nodeId: params.id,
        lineage_type: options.lineageType,
        successor_depth: options.successor_depth,
        predecessor_depth: options.predecessor_depth,
      });
      setLineage(data.lineage);
      setRootAsset(data.root_asset);
    } else if (lineageFetchType?.type === "project") {
      if (
        // don't refetch if the file is a sql file
        !lineageFetchType.data.filePath.includes(".sql") ||
        // or if the file is already loaded in the editor
        (shouldCheckLineageData &&
          lineageData[lineageFetchType.data.filePath]?.data)
      ) {
        return;
      }

      setLineageData((prev) => ({
        ...prev,
        [lineageFetchType.data.filePath]: {
          isLoading: true,
          data: null,
          error: null,
          showColumns: options.asset_only,
        },
      }));

      const data = await getProjectBasedLineage({
        branchId: lineageFetchType.data.branchId,
        filePath: lineageFetchType.data.filePath,
        lineage_type: options.lineageType,
        successor_depth: options.successor_depth,
        predecessor_depth: options.predecessor_depth,
        asset_only: options.asset_only,
      });

      setLineage(data.lineage);
      setRootAsset(data.root_asset);
      setLineageData((prev) => ({
        ...prev,
        [lineageFetchType.data.filePath]: {
          isLoading: false,
          data: data.lineage,
          error: null,
          showColumns: options.asset_only,
        },
      }));
    }
  };

  const onLineageFetchTypeChange = () => {
    if (lineageFetchType === null) {
      setLineage(null);
      setRootAsset(null);
      return;
    }
  };
  useEffect(onLineageFetchTypeChange, [lineageFetchType]);

  const onPathnameChange = () => {
    if (isAssetLineage) {
      setLineageFetchType({ type: "asset", data: { nodeId: params.id } });
    } else if (isProjectLineage) {
      setLineageFetchType({
        type: "project",
        data: { branchId, filePath: activeFile?.node.path || "" },
      });
      setLineage(lineageData[activeFile?.node.path || ""]?.data);
    } else {
      setLineageFetchType(null);
    }
  };
  useEffect(onPathnameChange, [pathname, params, activeFile, branchId]);

  useEffect(() => {
    setFocusedAsset(rootAsset);
    setAssetPreview(rootAsset);
  }, [rootAsset]);

  return (
    <LineageViewContext.Provider
      value={{
        lineage,
        lineageOptions,
        updateGraph,
        isLineageOptionsPanelOpen,
        setIsLineageOptionsPanelOpen,
        isTableOnly,
        isLoading,
        isLoadingColumns,
        isFilterOpen,
        toggleFilter,
        error,
        selectedColumn,
        hoveredColumn,
        expandedNodes,
        hoveredNode,
        hoveredEdge,
        selectedEdge,
        reactFlowWrapper,
        modelsMap,
        handleSelectColumn,
        handleExpandNode,
        handleColumnHover,
        onTableHeaderClick,
        onMouseEnterNode,
        onMouseLeaveNode,
        updateHoveredEdge,
        updateSelectedEdge,
        rootAsset,
        isLineageLevelSelectorOpen,
        setIsLineageLevelSelectorOpen,
        setLineageOptionsAndRefetch,
      }}
    >
      {children}
    </LineageViewContext.Provider>
  );
}

type LineageViewProps = {
  style?: React.CSSProperties;
};

export function LineageView(props: LineageViewProps) {
  const ErrorFallback = () => (
    <Alert variant="default">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Something went wrong</AlertTitle>
      <AlertDescription>Contact support@turntable.so</AlertDescription>
    </Alert>
  );

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        maxWidth: "100%",
        height: "96vh",
        ...props.style,
      }}
    >
      <ErrorBoundary
        fallback={
          <div className="bg-muted flex flex-col h-full text-muted-foreground font-semibold  justify-center  items-center">
            <div className="max-w-[550px]">
              <ErrorFallback />
            </div>
          </div>
        }
      >
        <ReactFlowProvider>
          <ColumnLineage />
        </ReactFlowProvider>
      </ErrorBoundary>
    </div>
  );
}
