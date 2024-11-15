import "@xyflow/react/dist/style.css";

import React, {
  useContext,
  useEffect,
  useLayoutEffect,
  useMemo,
  useState,
} from "react";
import {
  ReactFlow,
  Background,
  Panel,
  type ReactFlowInstance,
  useNodesInitialized,
} from "@xyflow/react";

import { getColumnLineageForAsset } from "../../lib/lineage";
import ColumnConnectionEdge, {
  AsIsLabel,
  E2ELabel,
  FilterLabel,
  GroupByLabel,
  JoinKeyLabel,
  TransformLabel,
} from "./ColumnConnectionEdge";
import ColumnLineageNode from "./ColumnLineageNode";
import ErrorNode from "./ErrorNode";
import { LineageViewContext } from "./LineageView";
import LoadingNode from "./LoadingNode";
import buildLineageReactFlow from "./renderLineage";
import { FilterPanel } from "./FilterPanel";
import "./lineage.css";
import { Loader2 } from "lucide-react";
import { useAppContext } from "../../contexts/AppContext";
import { LineageControls } from "./LineageControls";
import LineageOptionsPanel from "./LineageOptionsPanel";

const nodeTypes = {
  custom: ColumnLineageNode,
  loading: LoadingNode,
  error: ErrorNode,
};

export type LineageEdgeType =
  | "filter"
  | "group_by"
  | "join_key"
  | "e2e"
  | "as_is"
  | "transform";

const allEdgeTypes = [
  { type: "filter", label: "Filter", labelComponent: FilterLabel },
  { type: "group_by", label: "Group by", labelComponent: GroupByLabel },
  { type: "join_key", label: "Join key", labelComponent: JoinKeyLabel },
  { type: "transform", label: "Modify", labelComponent: TransformLabel },
  { type: "as_is", label: "Select as is", labelComponent: AsIsLabel },
  { type: "e2e", label: "End-to-end", labelComponent: E2ELabel },
];

const edgeTypes = {
  column_connection_edge: ColumnConnectionEdge,
};

const ColumnLineageFlow = () => {
  const [reactFlowInstance, setReactFlowInstance] =
    useState<ReactFlowInstance | null>(null);
  const nodesInitialized = useNodesInitialized();

  const {
    error,
    lineage,
    selectedColumn,
    hoveredColumn,
    expandedNodes,
    hoveredNode,
    updateHoveredEdge,
    updateSelectedEdge,
    reactFlowWrapper,
    isFilterOpen,
    toggleFilter,
    setIsLineageOptionsPanelOpen,
  } = useContext(LineageViewContext);

  const { isLineageLoading, setIsLineageLoading } = useAppContext();

  const onReactFlowInit = (reactFlowInstance: ReactFlowInstance) => {
    setReactFlowInstance(reactFlowInstance);
  };

  useEffect(() => {
    if (lineage) {
      setIsLineageLoading(false);
    }
  }, [lineage]);

  const columnLineage: any = useMemo(() => {
    if (lineage) {
      return getColumnLineageForAsset({
        assetId: lineage.asset_id,
        links: lineage.asset_links,
        nodes: lineage.assets,
        columnLinks: lineage.column_links,
      });
    }
    return null;
  }, [lineage]);

  const { nodes, edges } = useMemo(() => {
    let nodes = [] as any;
    let edges = [] as any;

    if (error) {
      nodes = [
        {
          id: "error-node",
          type: "error",
          position: { x: 0, y: 0 },
        },
      ];
      edges = [];

      return {
        nodes,
        edges,
        presentEdgeTypes: [],
      };
    }

    if (columnLineage) {
      const { finalNodes, filteredEdges, tableEdges } = buildLineageReactFlow({
        columnLineage,
        selectedColumn,
        hoveredColumn: hoveredColumn,
        expandedNodes,
        hoveredNode,
      }) as any;
      nodes = finalNodes;
      edges = [...filteredEdges, ...tableEdges] as any;
    }

    if (nodes.length === 0 && edges.length === 0) {
      nodes = [
        {
          id: "error-node",
          type: "error",
          position: { x: 0, y: 0 },
        },
      ];
    }
    return {
      nodes,
      edges,
    };
  }, [
    columnLineage,
    error,
    selectedColumn,
    expandedNodes,
    hoveredNode,
    hoveredColumn,
  ]);

  useLayoutEffect(() => {
    reactFlowInstance?.fitView({
      padding: 0.2,
    });
  }, [nodesInitialized, reactFlowInstance]);

  return (
    <ReactFlow
      onlyRenderVisibleElements={true}
      ref={reactFlowWrapper}
      key={lineage.asset_id}
      nodes={nodes}
      edges={edges}
      edgeTypes={edgeTypes}
      onEdgeMouseEnter={(e, edge) => {
        if (edge.type !== "column_connection_edge") {
          return;
        }

        if (!reactFlowInstance) {
          return;
        }

        const position = reactFlowInstance.screenToFlowPosition({
          x: e.clientX + 8,
          y: e.clientY,
        });

        updateHoveredEdge({
          ...edge,
          mousePosition: position,
        });
      }}
      onEdgeMouseLeave={() => updateHoveredEdge(null)}
      onEdgeClick={(e, edge) => {
        updateHoveredEdge(null);

        if (edge.type !== "column_connection_edge") {
          updateSelectedEdge(null);
          return;
        }

        if (!reactFlowInstance) {
          return;
        }

        const position = reactFlowInstance?.screenToFlowPosition({
          x: e.clientX + 8,
          y: e.clientY,
        });

        updateSelectedEdge({
          ...edge,
          mousePosition: position,
        });
      }}
      onPaneClick={() => {
        updateHoveredEdge(null);
        updateSelectedEdge(null);

        if (isFilterOpen) {
          toggleFilter();
        }

        setIsLineageOptionsPanelOpen(false);
      }}
      minZoom={0.1}
      defaultViewport={{
        x: 100,
        y: 60,
        zoom: 1,
      }}
      onInit={onReactFlowInit}
      attributionPosition="top-right"
      nodeTypes={nodeTypes}
      proOptions={{
        account: "paid-pro",
        hideAttribution: true,
      }}
    >
      <LineageOptionsPanel />
      <LineageControls />
      <FilterPanel />
      {isLineageLoading && (
        <Panel
          className="flex flex-col w-full h-full items-center justify-center"
          position="top-left"
        >
          <div>
            <Loader2 className="mr-2 h-8 w-8 animate-spin opacity-50" />
          </div>
        </Panel>
      )}
      <Background className="bg-zinc-200" />
    </ReactFlow>
  );
};

export default ColumnLineageFlow;
