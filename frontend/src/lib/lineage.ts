// @ts-nocheck
type LineageNodes = {
  id: string;
  name: string;
  columns: string[];
  relationshipToModel: "left" | "right" | "self" | "unknown";
};

export type Edge = {
  connection_types: string;
  source: string;
  target: string;
};

export type ColumnLineage = {
  nodes: LineageNodes[];
  columnEdges: Edge[];
  tableEdges: Array<{
    source: string;
    target: string;
  }>;
  originalFilePaths: {
    [modelId: string]: string;
  };
};

const buildTableLineage = ({
  links,
  currentModelId,
  nodes,
  columnLinks,
}: {
  links: any;
  currentModelId: string;
  nodes: any[];
  columnLinks: any[];
}) => {
  const edges = links;

  const processedEdges = links
    .map((edge) => ({
      id: edge.id,
      type: "default",
      markerEnd: { type: "arrow", fill: "#888888" },
      animated: false,
      source: `${edge.source_id}`,
      sourceHandle: `${edge.source_id}-source`,
      target: `${edge.target_id}`,
      targetHandle: `${edge.target_id}-target`,
      interactionWidth: 0,
      focusable: false,
      style: {
        stroke: "#888888",
        strokeWidth: 2,
      },
    }))
    .sort((a, b) => {
      return a.id.localeCompare(b.id);
    });
  const processedNodes = nodes
    .map((node: any) => {
      let relationshipToModel = "unknown";

      if (node.id === currentModelId) {
        relationshipToModel = "self";
      } else if (edges.find((edge: any) => edge.source_id === node.id)) {
        relationshipToModel = "left";
      } else if (edges.find((edge: any) => edge.target_id === node.id)) {
        relationshipToModel = "right";
      }
      const columns = node.columns;
      const name = node.unique_name || node.name;
      return {
        id: node.id,
        name,
        type: "custom",
        data: {
          relationshipToModel,
          name,
          originalFilePath: "<UNSET>",
          asset_type: node.type,
          resource_type: node.config?.dialect || node.resource_type,
          allColumns: columns
            .map((column: any) => {
              return {
                columnId: column.id,
                hasEdges:
                  columnLinks.filter(
                    (edge: any) =>
                      edge.source_id === column.id ||
                      edge.target_id === column.id,
                  ).length > 0,
                label: column.name,
                type: column.type,
              };
            })
            .sort((a, b) => {
              // sort by whether or not the column has edges
              if (a.hasEdges && !b.hasEdges) {
                return -1;
              }
              if (!a.hasEdges && b.hasEdges) {
                return 1;
              }

              return a.label.localeCompare(b.label);
            }),
        },
      };
    })
    .sort((a, b) => {
      return (a.name || "").localeCompare(b.name);
    });

  return {
    nodes: processedNodes,
    edges: processedEdges,
  };
};

export const getColumnLineageForAsset = ({
  assetId,
  links,
  nodes,
  columnLinks,
}: {
  assetId: string;
  links: any[];
  nodes: any[];
  columnLinks: any[];
}) => {
  const tableLineage = buildTableLineage({
    links,
    currentModelId: assetId,
    nodes,
    columnLinks,
  });

  //  we want to group qualify and havings into the 'filter' category for now
  const columnEdges = columnLinks.map((edge) => {
    const sourceParentNode = nodes.find((node: any) => {
      return node.columns.find((column: any) => column.id === edge.source_id);
    });
    const targetParentNode = nodes.find((node: any) => {
      return node.columns.find((column: any) => column.id === edge.target_id);
    });
    let sourceColumn = {};
    let targetColumn = {};
    if (sourceParentNode) {
      sourceColumn = sourceParentNode.columns.find(
        (column: any) => column.id === edge.source_id,
      );
    }
    if (targetParentNode) {
      targetColumn = targetParentNode.columns.find(
        (column: any) => column.id === edge.target_id,
      );
    }
    return {
      id: edge.id,
      type: "column_connection_edge",
      source: `${sourceParentNode?.id}`,
      sourceHandle: `${edge.source_id}-source`,
      target: `${targetParentNode?.id}`,
      targetHandle: `${edge.target_id}-target`,
      zIndex: 5,
      data: {
        ntype: Array.from(
          new Set(
            (edge.connection_types ?? ["e2e"]).map((type) =>
              ["having", "qualify"].includes(type) ? "filter" : type,
            ),
          ),
        ),
        sourceColumnName: sourceColumn.name,
        targetColumnName: targetColumn.name,
      },
    };
  });

  console.log({ columnEdges, nodes: tableLineage.nodes });

  return {
    nodes: tableLineage.nodes,
    tableEdges: tableLineage.edges,
    columnEdges,
    originalFilePaths: [],
  };
};

export function getVisibleEdges(columnId: string, edges: any[]) {
  let visited = new Set<string>();
  const outboundEdges = getDirectedVisibleEdges(columnId, edges, visited, true);

  // Resetting the visited set to traverse in the opposite direction.
  visited = new Set<string>();
  const inboundEdges = getDirectedVisibleEdges(columnId, edges, visited, false);

  return [...outboundEdges, ...inboundEdges];
}

function getDirectedVisibleEdges(
  columnId: string,
  edges: any[],
  visited: Set<string>,
  isOutbound: boolean,
): any[] {
  if (visited.has(columnId)) return [];
  visited.add(columnId);

  const relevantEdges = edges.filter((edge) =>
    isOutbound
      ? edge.sourceHandle === `${columnId}-source`
      : edge.targetHandle === `${columnId}-target`,
  );

  let allEdges = [...relevantEdges];

  for (const edge of relevantEdges) {
    const relatedColumn = getRelatedColumn(edge, isOutbound);
    const otherEdges = edges.filter((e) => e !== edge);
    allEdges = [
      ...allEdges,
      ...getDirectedVisibleEdges(
        relatedColumn,
        otherEdges,
        visited,
        isOutbound,
      ),
    ];
  }

  return allEdges;
}

function getRelatedColumn(edge: any, isOutbound: boolean): string {
  return isOutbound
    ? `${edge.targetHandle}`.replace("-target", "")
    : `${edge.sourceHandle}`.replace("-source", "");
}
