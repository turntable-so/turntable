"use client";
import React, {useEffect, useRef, useState} from "react";
import {ErrorBoundary} from "react-error-boundary";
import {type Edge, ReactFlowProvider} from "reactflow";
import ColumnLineage from "./ColumnLineage";

import {AlertCircle} from "lucide-react";

import {getLineage, getProjectBasedLineage} from "../../app/actions/actions";
import {useAppContext} from "../../contexts/AppContext";
import {Alert, AlertDescription, AlertTitle} from "../ui/alert";

export function ErrorFallback() {
  return (
    <Alert variant="default">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Something went wrong</AlertTitle>
      <AlertDescription>Contact support@turntable.so</AlertDescription>
    </Alert>
  );
}

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
  setLineageOptionsAndRefetch: (options: LineageOptions) => void;
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

type BaseLineageViewProviderProps = {
  children: React.ReactNode;
  startingLineage: Lineage;
  rootAsset: Asset;
};

type LineagePageProps = BaseLineageViewProviderProps & {
  page: "lineage";
};

type EditorPageProps = BaseLineageViewProviderProps & {
  page: "editor";
  filePath: string;
  branchId: string;
};

type LineageViewProviderProps = LineagePageProps | EditorPageProps;

export function LineageViewProvider(props: LineageViewProviderProps) {
  const { children, startingLineage, rootAsset, page } = props;
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingColumns, setIsLoadingColumns] = useState(false);
  const [isTableOnly, setIsTableOnly] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lineage, setLineage] = useState<Lineage>(startingLineage);

  const [isLineageOptionsPanelOpen, setIsLineageOptionsPanelOpen] =
    useState(false);
  const [lineageOptions, setLineageOptions] = useState<LineageOptions>({
    predecessor_depth: 1,
    successor_depth: 1,
    lineageType: "all",
  });

  const { setIsLineageLoading } = useAppContext();

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

  const [modelsMap, setModelsMap] = useState<Record<string, any>>({});

  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [isLineageLevelSelectorOpen, setIsLineageLevelSelectorOpen] =
    useState(false);
  const toggleFilter = () => {
    setIsFilterOpen((prev) => !prev);
  };

  const reactFlowWrapper = useRef<HTMLDivElement>(null);

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

  async function getColumnLineage() {
    // setIsLoadingColumns(true);
    // // const data = request()
    // if ((data?.lineage?.links || []).length > 1) {
    //     console.log('webview.lineage.columns.success');
    // }
    // setIsLoadingColumns(false);
  }

  /**
   * Initial load:
   * 1. Get stored filter options
   * 2. Get lineage data
   */
  useEffect(() => {
    async function load() {
      setIsLoading(false);
    }

    load();
  }, []);

  useEffect(() => {
    if (isLoading) {
      return;
    }

    getColumnLineage();
  }, [isLoading]);

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

  if (isLoading) {
    return <div>loading</div>;
  }

  const setLineageOptionsAndRefetch = async (options: LineageOptions) => {
    setLineageOptions(options);
    setIsLineageLoading(true);

    if (page === "lineage") {
      const data = await getLineage({
        nodeId: rootAsset.id,
        successor_depth: options.successor_depth,
        predecessor_depth: options.predecessor_depth,
        lineage_type: options.lineageType,
      });
      setIsLineageLoading(false);
      setLineage(data.lineage);
    } else if (page === "editor") {
      setLineageOptions(options);
      setIsLineageLoading(true);
      const data = await getProjectBasedLineage({
        branchId: props.branchId,
        filePath: props.filePath,
        successor_depth: options.successor_depth,
        predecessor_depth: options.predecessor_depth,
      });
      console.log(data);
      setIsLineageLoading(false);
      setLineage(data.lineage);
    }
  };

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

type Lineage = {
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

type BaseLineageViewProps = {
  lineage: Lineage;
  rootAsset: Asset;
  style?: React.CSSProperties;
};

type LineagePageViewProps = BaseLineageViewProps & {
  page: "lineage";
};

type EditorLineageViewProps = BaseLineageViewProps & {
  page: "editor";
  filePath: string;
  branchId: string;
};

type LineageViewProps = LineagePageViewProps | EditorLineageViewProps;

export function LineageView(props: LineageViewProps) {
  const { lineage, rootAsset, style, page } = props;
  const { setFocusedAsset, setAssetPreview } = useAppContext();

  const LineageContent = () => (
    <div
      style={{
        position: "relative",
        width: "100%",
        maxWidth: "100%",
        height: "100vh",
        ...style,
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

  useEffect(() => {
    setFocusedAsset(rootAsset);
    setAssetPreview(rootAsset);
  }, [rootAsset, setFocusedAsset, setAssetPreview]);

  if (page === "editor") {
    return (
      <LineageViewProvider
        startingLineage={lineage}
        rootAsset={rootAsset}
        page="editor"
        filePath={props.filePath}
        branchId={props.branchId}
      >
        <LineageContent />
      </LineageViewProvider>
    );
  }

  if (page === "lineage") {
    return (
      <LineageViewProvider
        startingLineage={lineage}
        rootAsset={rootAsset}
        page="lineage"
      >
        <LineageContent />
      </LineageViewProvider>
    );
  }

  throw new Error("Invalid page prop");
}
