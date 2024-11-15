import React, { useContext, useMemo } from "react";
import {
  BaseEdge,
  EdgeLabelRenderer,
  type EdgeProps,
  getBezierPath,
  useEdges,
  useStoreApi,
} from "@xyflow/react";
import * as colors from "tailwindcss/colors";
import { LineageViewContext } from "./LineageView";

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
};

export function CustomEdge({
  id,
  source,
  sourceX,
  sourceY,
  target,
  targetX,
  targetY,
  data,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
}: EdgeProps) {
  const {
    hoveredColumn,
    hoveredEdge,
    selectedColumn,
    selectedEdge,
    updateSelectedEdge,
  } = useContext(LineageViewContext);
  const store = useStoreApi();
  const edges = useEdges();

  const { edgePath } = useMemo(() => {
    const [edgePath, labelX, labelY] = getBezierPath({
      sourceX,
      sourceY,
      sourcePosition,
      targetX,
      targetY,
      targetPosition,
    });

    return { edgePath, labelX, labelY };
  }, [sourceX, sourceY, sourcePosition, targetX, targetY, targetPosition]);

  const isHovered = hoveredEdge?.id === id;
  const isSelected = selectedEdge?.id === id;

  const edgeStyles = useMemo(() => {
    const isColumnInNodeHovered =
      hoveredColumn &&
      selectedColumn &&
      selectedColumn !== hoveredColumn.columnId;
    return {
      opacity: !selectedColumn ? 0.5 : 1,
      ...style,
      strokeWidth: isSelected || isHovered || isColumnInNodeHovered ? 4 : 2,
      stroke:
        data?.ntype.length === 1
          ? getStrokeColorForConnectionType(data.ntype[0])
          : `url(#multiColorGradient-${data?.sourceColumnName}-${data?.targetColumnName})`,

      strokeDasharray: edges.length > 100 ? "5,5" : "",
      zIndex: 10000,
    };
  }, [
    hoveredColumn,
    selectedColumn,
    selectedEdge,
    isHovered,
    isSelected,
    target,
    source,
    data,
    edges,
  ]);

  const detailsPosition = isSelected
    ? selectedEdge?.mousePosition
    : isHovered
      ? hoveredEdge?.mousePosition
      : null;

  return (
    <>
      {data.ntype.length > 1 && (
        <defs>
          <linearGradient
            gradientUnits="userSpaceOnUse"
            id={`multiColorGradient-${data?.sourceColumnName}-${data?.targetColumnName}`}
            x1="0%"
            y1="0%"
            x2="100%"
            y2="0%"
          >
            {data?.ntype.map((type, index) => {
              const offset = (index / (data?.ntype.length - 1)) * 100;
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
        </defs>
      )}

      <BaseEdge
        key={`${id}-${data.ntype.join("-")}`}
        path={edgePath}
        markerEnd={markerEnd}
        style={edgeStyles}
      />

      <EdgeLabelRenderer>
        {(isSelected || (isHovered && !selectedEdge)) && detailsPosition && (
          <div
            style={{
              position: "absolute",
              zIndex: 101,
              transform: `translate(${detailsPosition.x}px, ${detailsPosition.y}px)`,
              fontSize: 12,
              // everything inside EdgeLabelRenderer has no pointer events by default
              // if you have an interactive element, set pointer-events: all
              pointerEvents: "all",
              cursor: "default",
            }}
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
            }}
            onMouseEnter={(e) => {
              e.preventDefault();
              e.stopPropagation();
            }}
          >
            <div
              style={{ fontSize: "10px" }}
              className="z-100 min-w-[100px] rounded-lg pt-1 pb-2 px-2
                  bg-white dark:bg-zinc-800
                  border border-blue-400 da border-solid
                  shadow-md
                "
            >
              <div className="flex justify-between">
                <div className="space-y-1 py-1">
                  {data.ntype.map((type, index) => (
                    <div
                      key={`${type}-${index}`}
                      className="flex space-x-1 items-center"
                    >
                      <ConnectionTypeLabel type={type} />
                      <div>{getLabelName(type)}</div>
                    </div>
                  ))}
                </div>
                {isSelected && (
                  <div className="font-bold hover:opacity-50">
                    <span
                      className="codicon codicon-close cursor-pointer"
                      onClick={(e) => {
                        e.stopPropagation();
                        store.getState().resetSelectedElements();
                        updateSelectedEdge(null);
                      }}
                    />
                  </div>
                )}
              </div>
              <div>
                <div>
                  from:{" "}
                  <span className="font-mono font-bold truncate">
                    {data.sourceColumnName}
                  </span>
                </div>
                <div>
                  to:{" "}
                  <span className="font-mono font-bold truncate">
                    {data.targetColumnName}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </EdgeLabelRenderer>
    </>
  );
}

export default React.memo(CustomEdge);
