// @ts-nocheck
import {
  type ColumnLineage,
  type Edge,
  getVisibleEdges,
} from "../../lib/lineage";

import dagre from "@dagrejs/dagre";
import type { ColumnWithPosition } from "../../app/contexts/LineageView";

const maxNodeHeight = 260;

const getLayoutedElements = (nodes, edges, hoveredNode) => {
  if (!nodes.length || !edges.length) {
    return { nodes, edges };
  }

  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));

  const nodeWidth = 260;
  const baseNodeHeight = 52;
  const columnHeight = 24;

  dagreGraph.setGraph({
    rankdir: "LR",
    align: "UL",
    ranksep: 150,
  });

  nodes.forEach((node) => {
    const numColumns = node.data.collapsed
      ? node.data.filteredColumns.length
      : node.data.allColumns.length;

    const thisNodeHeight = Math.min(
      baseNodeHeight + numColumns * columnHeight,
      maxNodeHeight,
    );

    let hoveredYPos = null;

    if (hoveredNode && hoveredNode.nodeId === node.id) {
      hoveredYPos = hoveredNode.yPos;
    }

    const y =
      hoveredYPos != null ? hoveredYPos + thisNodeHeight / 2 : undefined;

    dagreGraph.setNode(node.id, {
      width: nodeWidth,
      height: thisNodeHeight,
      y,
    });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);
  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    node.targetPosition = "left";
    node.sourcePosition = "right";

    const numColumns = node.data.collapsed
      ? node.data.filteredColumns.length
      : node.data.allColumns.length;

    const thisNodeHeight = Math.min(
      baseNodeHeight + numColumns * columnHeight,
      maxNodeHeight,
    );

    let hoveredYPos = null;

    if (hoveredNode && hoveredNode.nodeId === node.id) {
      hoveredYPos = hoveredNode.yPos;
    }
    node.position = {
      x: nodeWithPosition.x - nodeWidth / 2,
      y:
        hoveredYPos != null
          ? hoveredYPos
          : Math.max(0, nodeWithPosition.y - thisNodeHeight / 2),
    };

    return node;
  });

  return { nodes, edges };
};

type Args = {
  columnLineage: ColumnLineage;
  selectedColumn: string | null;
  hoveredColumn: ColumnWithPosition | null;
  expandedNodes: string[];
  hoveredNode: {
    nodeId: string;
    yPos: number;
  } | null;
};

export default function buildLineageReactFlow({
  columnLineage,
  selectedColumn,
  hoveredColumn,
  expandedNodes,
  hoveredNode,
}: Args) {
  const edges = columnLineage.columnEdges;

  const filteredEdges = selectedColumn
    ? getVisibleEdges(selectedColumn, edges)
    : hoveredColumn
      ? getVisibleEdges(hoveredColumn.columnId, edges)
      : [];

  // gets unique table edges from column edges
  const tableEdges = columnLineage.tableEdges.map((edge: any) => {
    const highlight =
      hoveredNode?.nodeId === edge.source ||
      hoveredNode?.nodeId === edge.target;

    return {
      ...edge,
      zIndex: highlight ? 5 : -1,
      style: {
        ...edge.style,
        opacity: selectedColumn ? 0.5 : 1,
      },
    };
  });

  const nodes = columnLineage.nodes;

  const getFilteredColumns = (
    node: any,
    selectedColumn: string | null,
    hoveredColumn: ColumnWithPosition | null,
  ) => {
    if (selectedColumn) {
      return node.data.allColumns.filter(
        (column: any) =>
          filteredEdges.find(
            (edge) =>
              edge.sourceHandle === `${column.columnId}-source` ||
              edge.targetHandle === `${column.columnId}-target`,
          ) || column.columnId === selectedColumn,
      );
    }
    if (hoveredColumn) {
      return node.data.allColumns.filter(
        (column: any) =>
          filteredEdges.find(
            (edge) =>
              edge.sourceHandle === `${column.columnId}-source` ||
              edge.targetHandle === `${column.columnId}-target`,
          ) || column.columnId === hoveredColumn.columnId,
      );
    }

    return [];
  };

  const nodesWithDisplayColumns = nodes.map((node: any) => {
    const filteredColumns = getFilteredColumns(
      node,
      selectedColumn,
      hoveredColumn,
    );

    if (!node.position) {
      node.position = { x: 0, y: 0 };
    }
    return {
      ...node,
      data: {
        ...node.data,
        collapsed: !expandedNodes.includes(node.id),
        filteredColumns,
        allColumns: node.data.allColumns.map((column: any) => ({
          ...column,
          hasFilteredEdges:
            filteredColumns.find((c: any) => c.columnId === column.columnId) !=
            null,
        })),
      },
    };
  });

  const { nodes: layoutedNodes } = getLayoutedElements(
    nodesWithDisplayColumns,
    tableEdges,
    hoveredNode,
  );

  // for (const node of nodesWithDisplayColumns) {
  //   for (const column of node.data.filteredColumns) {
  //     const columnId = column.columnId;
  //   }
  // }

  // Turn off animated edges when there are more than 100 edges to be rendered.
  const finalColumnEdges = filteredEdges.map((edge: Edge) => ({
    ...edge,
    animated: filteredEdges.length < 100,
  }));

  return {
    finalNodes: layoutedNodes,
    filteredEdges: finalColumnEdges,
    tableEdges,
  };
}
