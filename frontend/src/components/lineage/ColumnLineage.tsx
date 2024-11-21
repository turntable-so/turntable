import "@xyflow/react/dist/style.css";

import type React from "react";
import {
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
import ColumnConnectionEdge from "./ColumnConnectionEdge";
import ColumnLineageNode from "./ColumnLineageNode";
import ErrorNode from "./ErrorNode";
import { LineageViewContext } from "@/app/contexts/LineageView";
import LoadingNode from "./LoadingNode";
import buildLineageReactFlow from "./renderLineage";
import { FilterPanel } from "./FilterPanel";
import "./lineage.css";
import { Loader2 } from "lucide-react";
import { useAppContext } from "../../contexts/AppContext";
import { LineageControls } from "./LineageControls";
import LineageOptionsPanel from "./LineageOptionsPanel";
import { useTheme } from "next-themes";
import { useFiles } from "@/app/contexts/FilesContext";
import { usePathname } from "next/navigation";

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

const edgeTypes = {
  column_connection_edge: ColumnConnectionEdge,
};

const ColumnLineageFlow = () => {
  const [reactFlowInstance, setReactFlowInstance] =
    useState<ReactFlowInstance | null>(null);
  const nodesInitialized = useNodesInitialized();

  const { resolvedTheme } = useTheme();
  const { lineageData, branchId, activeFile, files, openFile } = useFiles();
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

  const pathname = usePathname();
  const isInEditor = pathname.includes("editor");
  const showFilterPanel =
    isInEditor && activeFile
      ? !lineageData[activeFile.node.path]?.showColumns
      : true;

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

  const handleCtrlClickOnNode = (node: any) => {
    if (!files || !files[0]?.children || !branchId) {
      return;
    }
    const nodeNameParts = node.name.split(".");
    const targetFileName = nodeNameParts[nodeNameParts.length - 1];

    const modelsFolder = files[0]?.children.find(
      (child) => child.path === "models",
    );

    const findFileByName = (items: any[]): any => {
      for (const item of items) {
        const itemBaseName = item.name.split(".")[0];
        if (item.type === "file" && itemBaseName === targetFileName) {
          return item;
        }
        if (item.children) {
          const found = findFileByName(item.children);
          if (found) return found;
        }
      }
      return null;
    };

    const targetFile = modelsFolder?.children
      ? findFileByName(modelsFolder.children)
      : null;

    if (targetFile) {
      openFile(targetFile);
    }
  };

  const onNodeClick = (event: React.MouseEvent, node: any) => {
    if (event.ctrlKey || event.metaKey) {
      handleCtrlClickOnNode(node);
    }
  };

  return (
    <ReactFlow
      onlyRenderVisibleElements={true}
      ref={reactFlowWrapper}
      // key={lineage?.asset_id || ""}
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
      onNodeClick={onNodeClick}
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
      {showFilterPanel && <FilterPanel />}
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
      <Background
        bgColor={resolvedTheme === "dark" ? "black" : "white"}
        size={1.5}
      />
    </ReactFlow>
  );
};

export default ColumnLineageFlow;
