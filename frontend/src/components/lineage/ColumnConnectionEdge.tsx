import React, { useContext, useMemo, CSSProperties, MouseEvent } from "react";
import {
  BaseEdge,
  EdgeLabelRenderer,
  type EdgeProps,
  getBezierPath,
  useEdges,
  useStoreApi,
  Position,
  XYPosition,
  Edge,
  Node,
  ReactFlowState,
  Connection,
} from "@xyflow/react";
import * as colors from "tailwindcss/colors";
import { LineageViewContext } from "../../app/contexts/LineageView";

type EdgeData = {
  ntype: string[];
  sourceColumnName: string;
  targetColumnName: string;
  [key: string]: unknown;
};

type CustomEdge = Edge<EdgeData>;

type ColumnEdgeProps = Omit<EdgeProps, 'data'> & {
  data: EdgeData;
};

interface EdgeGradientsProps {
  edges: CustomEdge[];
}

function getStrokeColorForConnectionType(type: string) {
  switch (type) {
    case "filter":
      return colors.amber[500];
    case "transform":
      return colors.red[500];
    case "group_by":
      return colors.green[500];
    case "as_is":
      return colors.blue[500];
    case "join_key":
      return colors.purple[500];
    case "e2e":
      return colors.gray[500];
    default:
      return colors.rose[400];
  }
}

export const FilterLabel = () => (
  <div
    title={getLabelName("filter")}
    className="opacity-90 bg-amber-500 h-4 w-4 border-white border-solid border-2 rounded-sm shadow-md flex items-center justify-center text-white text-xs font-medium"
  >
    F
  </div>
);
export const TransformLabel = () => (
  <div
    title={getLabelName("transform")}
    className="opacity-90 bg-red-500 h-4 w-4 border-white border-solid border-2 rounded-sm shadow-md flex items-center justify-center text-white text-xs font-medium"
  >
    M
  </div>
);
export const GroupByLabel = () => (
  <div
    title={getLabelName("group_by")}
    className="opacity-90 bg-green-500 h-4 w-4 border-white border-solid border-2 rounded-sm shadow-md flex items-center justify-center text-white text-xs font-medium"
  >
    G
  </div>
);
export const AsIsLabel = () => (
  <div
    title={getLabelName("as_is")}
    className="opacity-90 bg-blue-500 h-4 w-4 border-white border-solid border-2 rounded-sm shadow-md flex items-center justify-center text-white text-xs font-medium"
  >
    S
  </div>
);
export const JoinKeyLabel = () => (
  <div
    title={getLabelName("join_key")}
    className="opacity-90 bg-purple-500 h-4 w-4 border-white border-solid border-2 rounded-sm shadow-md flex items-center justify-center text-white text-xs font-medium"
  >
    J
  </div>
);

export const UnknownKeyLabel = () => (
  <div className="opacity-90 bg-rose-400 h-4 w-4 rounded-sm flex items-center justify-center text-white text-xs font-medium">
    U
  </div>
);
export const E2ELabel = () => (
  <div
    title={getLabelName("e2e")}
    className="opacity-90 bg-gray-500 h-4 w-4 border-white border-solid border-2 rounded-sm shadow-md flex items-center justify-center text-white text-xs font-medium"
  >
    E
  </div>
);

export const ConnectionTypeLabel = ({ type }: { type: string }) => {
  switch (type) {
    case "filter":
      return <FilterLabel />;
    case "transform":
      return <TransformLabel />;
    case "group_by":
      return <GroupByLabel />;
    case "as_is":
      return <AsIsLabel />;
    case "join_key":
      return <JoinKeyLabel />;
    default:
      return <UnknownKeyLabel />;
  }
};

export const getLabelName = (type) => {
  switch (type) {
    case "filter":
      return "Filter";
    case "transform":
      return "Modify";
    case "group_by":
      return "Group by";
    case "as_is":
      return "Select as is";
    case "join_key":
      return "Join key";
    case "e2e":
      return "End to end";
    default:
      return "Unknown";
  }
}

const EdgeGradients: React.FC<EdgeGradientsProps> = React.memo(({ edges }) => {
  const store = useStoreApi();

  return (
    <defs>
      {edges
        .filter((edge) => {
          const data = edge.data;
          return Array.isArray(data?.ntype) && data.ntype.length > 1;
        })
        .map((edge) => {
          const { data, source, target } = edge;
          if (!data) return null;

          // Get nodes from the store
          const state = store.getState() as ReactFlowState;
          const nodes = state.nodes as Node[];
          const sourceNode = nodes.find((node: Node) => node.id === source);
          const targetNode = nodes.find((node: Node) => node.id === target);

          if (!sourceNode || !targetNode) return null;

          // Calculate positions based on node positions
          const sourcePos = {
            x: sourceNode.position.x + (sourceNode.width ?? 0) / 2,
            y: sourceNode.position.y + (sourceNode.height ?? 0) / 2,
          };
          const targetPos = {
            x: targetNode.position.x + (targetNode.width ?? 0) / 2,
            y: targetNode.position.y + (targetNode.height ?? 0) / 2,
          };

          return (
            <linearGradient
              key={`gradient-${source}-${target}`}
              gradientUnits="userSpaceOnUse"
              id={`multiColorGradient-${data.sourceColumnName}-${data.targetColumnName}`}
              x1={sourcePos.x}
              y1={sourcePos.y}
              x2={targetPos.x}
              y2={targetPos.y}
            >
              {data.ntype.map((type: string, index: number) => {
                const offset = (index / (data.ntype.length - 1)) * 100;
                const color = getStrokeColorForConnectionType(type);
                return (
                  <stop
                    key={index}
                    offset={`${offset}%`}
                    style={{ stopColor: color, stopOpacity: 1 }}
                  />
                );
              })}
            </linearGradient>
          );
        })}
    </defs>
  );
});

export function ColumnConnectionEdge({
  id,
  source,
  target,
  style = {},
  markerEnd,
  data,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  ...props
}: ColumnEdgeProps) {
  const {
    hoveredColumn,
    hoveredEdge,
    selectedColumn,
    selectedEdge,
    updateSelectedEdge,
  } = useContext(LineageViewContext);
  const edges = useEdges<CustomEdge>();

  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition: sourcePosition ?? Position.Right,
    targetPosition: targetPosition ?? Position.Left,
  });

  const isHovered = hoveredEdge?.id === id;
  const isSelected = selectedEdge?.id === id;

  const edgeStyles: CSSProperties = {
    ...(style as CSSProperties),
    stroke: data.ntype.length === 1
      ? getStrokeColorForConnectionType(data.ntype[0])
      : `url(#multiColorGradient-${data.sourceColumnName}-${data.targetColumnName})`,
    strokeWidth: isHovered || isSelected ? 2 : 1,
    opacity: !selectedColumn ? 0.5 : 1,
    strokeDasharray: edges.length > 100 ? "5,5" : "",
    zIndex: 10000,
  };

  const detailsPosition = {
    x: labelX,
    y: labelY,
  };

  const handleEdgeClick = (event: MouseEvent<SVGPathElement>) => {
    event.stopPropagation();
    if (updateSelectedEdge) {
      const selectedEdge: Edge<EdgeData> & { mousePosition: { x: number; y: number } } = {
        id,
        source,
        target,
        sourceHandle: null,
        targetHandle: null,
        type: 'custom',
        data,
        selected: true,
        animated: false,
        hidden: false,
        deletable: true,
        selectable: true,
        focusable: true,
        label: '',
        interactionWidth: 20,
        zIndex: 0,
        mousePosition: {
          x: event.clientX,
          y: event.clientY,
        },
      };
      updateSelectedEdge(selectedEdge);
    }
  };

  return (
    <>
      <EdgeGradients edges={edges} />
      <path
        id={id}
        className="react-flow__edge-path"
        d={edgePath}
        markerEnd={markerEnd}
        style={edgeStyles}
        onClick={handleEdgeClick}
      />
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${detailsPosition.x}px,${detailsPosition.y}px)`,
            pointerEvents: 'all',
          }}
          className="nodrag nopan"
        >
          {data.ntype.map((type: string, index: number) => (
            <span
              key={`${id}-${type}-${index}`}
              className="px-2 py-1 text-xs rounded bg-white shadow-sm"
              style={{
                color: getStrokeColorForConnectionType(type),
                marginRight: index < data.ntype.length - 1 ? '4px' : 0,
              }}
            >
              {getLabelName(type)}
            </span>
          ))}
        </div>
      </EdgeLabelRenderer>
    </>
  );
}

export default React.memo(ColumnConnectionEdge);
