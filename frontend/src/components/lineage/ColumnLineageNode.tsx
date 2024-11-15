// @ts-nocheck
import type React from "react";
import {
  type PropsWithChildren,
  memo,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  Handle,
  Position,
  useReactFlow,
  useUpdateNodeInternals,
} from "@xyflow/react";
import { useAppContext } from "../../contexts/AppContext";
import { getAssetIcon } from "../../lib/utils";
import { ColumnTypeIcon } from "../ColumnTypeIcon";
import { Tooltip, TooltipContent, TooltipTrigger } from "../ui/tooltip";
import { LineageViewContext } from "./LineageView";
// import { useHotkeys } from 'react-hotkeys-hook';

const ModelIcon = () => (
  <div className="min-w-[1rem] h-4">
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1}
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9"
      />
    </svg>
  </div>
);

function Column({ label, handleId, type }) {
  return (
    <div className="custom-node__select relative">
      <div className="flex flex-row gap-1.5 items-center truncate text-ellipsis">
        <div>
          <ColumnTypeIcon dataType={type} className="size-3" />
        </div>
        <div className="font-semibold font-mono">{label}</div>
        <div className="truncate text-muted-foreground text-ellipsis">
          {type}
        </div>
      </div>
      <Handle
        isConnectable={false}
        onConnect={(params) => console.log("handle onConnect", params)}
        id={`${handleId}-target`}
        type="target"
        position={Position.Left}
      />
      <Handle
        isConnectable={false}
        onConnect={(params) => console.log("handle onConnect", params)}
        id={`${handleId}-source`}
        type="source"
        position={Position.Right}
      />
    </div>
  );
}

function Header({
  tableId,
  type,
  tableName,
  hasFile,
  isLoading,
  isExpanded,
  resourceType,
  columnCount,
}: any) {
  return (
    <div className="flex justify-between gap-1">
      <Handle
        isConnectable={false}
        id={`${tableId}-target`}
        type="target"
        position={Position.Left}
      />

      <div
        className={`font-medium items-center truncate text-ellipsis flex gap-1`}
      >
        {isLoading ? (
          <div />
        ) : (
          <>
            <div className="mr-0.5">{getAssetIcon(type, resourceType)}</div>
            {/* {hasFile && (
                            <div
                                className={`rounded-sm cursor-pointer hidden group-hover:block hover:opacity-50
            `}
                            >
                                {isExpanded ? (
                                    <ChevronUp className='w-4 h-4' />
                                ) : (
                                    <ChevronRight className='w-4 h-4' />
                                )}
                            </div>
                        )} */}
          </>
        )}
        <div className="flex gap-0 flex-col overflow-auto size-full">
          <Tooltip>
            <TooltipTrigger>
              <div className="font-mono font-semibold truncate">
                {tableName}
              </div>
            </TooltipTrigger>
            <TooltipContent>{tableName}</TooltipContent>
          </Tooltip>
          <div className="">{type}</div>
        </div>
      </div>

      <Handle
        isConnectable={false}
        onConnect={(params) => console.log("handle onConnect", params)}
        id={`${tableId}-source`}
        type="source"
        position={Position.Right}
        style={{ marginRight: "-7px" }}
      />
    </div>
  );
}

interface CodeLensActionProps {
  onClick: React.MouseEventHandler<HTMLDivElement> | undefined;
}

function CodeLensAction({
  children,
  onClick,
}: PropsWithChildren<CodeLensActionProps>) {
  return (
    <div
      className="text-[color:var(--vscode-editorCodeLens-foreground)] hover:text-[color:var(--vscode-textLink-activeForeground)] text-[10px] cursor-pointer"
      onClick={onClick}
    >
      {children}
    </div>
  );
}

function LineageNode({ id, data, yPos }: any) {
  const {
    isLoadingColumns,
    handleSelectColumn,
    handleColumnHover,
    onMouseLeaveNode,
    onTableHeaderClick,
    onMouseEnterNode,
    handleExpandNode,
    selectedColumn,
    reactFlowWrapper,
    modelsMap,
    hoveredNode,
    lineageData,
  } = useContext(LineageViewContext);

  const { fetchAssetPreview, assets } = useAppContext();

  const model = useMemo(() => {
    return modelsMap[id];
  }, [modelsMap]);

  const reactFlowInstance = useReactFlow();

  const onClick = useCallback(
    (columnId: string) => {
      handleSelectColumn(columnId);
    },
    [handleSelectColumn],
  );

  const onHover = useCallback(
    (
      columnId: string | null,
      e?: React.MouseEvent<HTMLDivElement, MouseEvent>,
    ) => {
      if (!reactFlowWrapper?.current) {
        return;
      }

      if (columnId != null && e) {
        const reactFlowBounds =
          reactFlowWrapper?.current?.getBoundingClientRect();
        const position = reactFlowInstance.screenToFlowPosition({
          x: e.clientX - reactFlowBounds.left + 8,
          y: e.clientY - reactFlowBounds.top,
        });

        handleColumnHover({
          columnId,
          mousePosition: position,
        });
      } else {
        handleColumnHover(null);
      }
    },
    [handleColumnHover],
  );

  const onHeaderClick = useCallback(
    (e) => {
      e.stopPropagation();
      onTableHeaderClick(id, data.originalFilePath);
    },
    [id, data.originalFilePath, onTableHeaderClick],
  );

  const onExpandButton = useCallback(() => {
    handleExpandNode(id);
  }, [id, handleExpandNode]);

  // useHotkeys('escape', () => {
  //     if (selectedColumn != null && selectedColumn.includes(id)) {
  //         handleSelectColumn(selectedColumn);
  //         return;
  //     }

  //     if (!data.collapsed) {
  //         handleExpandNode(id);
  //     }
  // });

  const errors = useMemo(() => {
    return [];
  }, [lineageData, id]);

  // When just edges are updated, nodes are not re-rendered.
  // This is the workaroud: https://github.com/wbkd/react-flow/issues/916
  const updateNode = useUpdateNodeInternals();
  useEffect(() => {
    updateNode(id);
  }, [data.filteredColumns]);

  const columnsToDisplay = data.collapsed
    ? data.filteredColumns
    : data.allColumns;

  const isWindows = navigator.userAgent.includes("Windows");

  const fileName = data.originalFilePath?.split(isWindows ? `\\` : "/").pop();

  const hasErrors = errors.length > 0;

  const isActiveResource = (lineageData as any)?.activeResource?.id === id;

  return (
    <div className="group">
      <div
        className={`cursor-pointer border-2 font-mono shadow-lg text-[12px] rounded-md
        border-solid ${isActiveResource ? "border-blue-400" : "border-gray-300 dark:border-zinc-700"}
        bg-muted w-72 max-h-72 overflow-y-scroll overflow-x-hidden relative
        ${columnsToDisplay.length > 10 ? "nowheel" : ""}
        ${
          selectedColumn != null &&
          data.filteredColumns?.length === 0 &&
          hoveredNode?.nodeId !== id
            ? "opacity-40"
            : ""
        }
        ${
          selectedColumn?.startsWith(`${id}.`)
            ? "border-blue-400"
            : "hover:border-[color:var(--vscode-button-secondaryHoverBackground)]"
        }
        ${
          hasErrors
            ? "border-red-400 hover:border-[color:var(--vscode-inputValidation-errorBorder)]"
            : ""
        }
        `}
        onScroll={() => {
          updateNode(id);
        }}
        onMouseEnter={() => {
          onMouseEnterNode(id, yPos);
        }}
        onMouseLeave={onMouseLeaveNode}
        onClick={onExpandButton}
      >
        {data.name && data.name.length > 27 && (
          <div className="flex absolute top-[-24px] left-0">
            <ModelIcon />
            <div className="text-xs">{data.name}</div>
          </div>
        )}
        <div
          onClick={() => fetchAssetPreview(id)}
          className={`sticky top-0 left-0 right-0
          bg-muted z-50
          py-3 px-2 border-t-0 border-l-0 border-r-0 ${
            columnsToDisplay.length > 0 ? "border-b-2 border-solid" : ""
          } font-bold text-title uppercase text-xs group`}
        >
          <Header
            tableId={id}
            tableName={data.name}
            type={data.asset_type}
            resourceType={data.resource_type}
            onCollapse={onExpandButton}
            onOpenFile={onHeaderClick}
            hasFile={data.originalFilePath != null}
            isExpanded={!data.collapsed}
            isLoading={isLoadingColumns}
            columnCount={data.allColumns.length}
          />
        </div>
        {columnsToDisplay.length > 0 && (
          <div className="pt-1 pb-2">
            {columnsToDisplay.map((column: any, index: number) => {
              return (
                <div
                  key={column.columnId}
                  onClick={(e) => {
                    e.stopPropagation();
                    column.hasEdges ? onClick(column.columnId) : undefined;
                  }}
                  onMouseEnter={(e) => onHover(column.columnId, e)}
                  onMouseLeave={(e) => onHover(null)}
                  className={`nodeColumn h-5 sticky top-[15px] left-0 right-0 bottom-[-15px]`}
                >
                  <div
                    className={`
                    ${column.hasEdges ? "cursor-pointer" : "cursor-not-allowed"}
                    px-2 rounded-md ${
                      selectedColumn === column.columnId
                        ? "bg-card"
                        : "hover:bg-card"
                    } ${
                      selectedColumn != null &&
                      !data.collapsed &&
                      !column.hasFilteredEdges &&
                      hoveredNode?.nodeId !== id
                        ? "opacity-40"
                        : column.hasEdges
                          ? "opacity-100"
                          : "opacity-40"
                    }
                  `}
                  >
                    <Column
                      index={index}
                      label={column.label}
                      type={column.type}
                      key={column.columnId}
                      nodeId={column.columnId}
                      handleId={column.columnId}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
      {hasErrors && (
        <CodeLensAction
          onClick={() => {
            // providerRequest('OPEN_PROBLEMS');
          }}
        >
          <div className="ml-1 mt-1 opacity-70 text-[color:var(--vscode-inputValidation-errorBorder)] flex gap-1 items-center hover:opacity-100">
            <span className="codicon codicon-error" />
            <div>{errors.length} errors</div>
          </div>
        </CodeLensAction>
      )}
    </div>
  );
}

export default memo(LineageNode);
