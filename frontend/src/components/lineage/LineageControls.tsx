import { Maximize, ZoomIn, ZoomOut } from "lucide-react";
import React, { useCallback, useContext } from "react";
import { Panel, useReactFlow, useViewport } from "@xyflow/react";
import { Button } from "../ui/button";
import { LineageViewContext } from "../../app/contexts/LineageView";

const buttonTailwindClasses = `p-1.5
  rounded-lg
  bg-[color:var(--vscode-editor-background)]
  hover:bg-[color:var(--vscode-button-secondaryHoverBackground)]
  border border-[color:var(--vscode-notificationCenter-border)] border-solid
  text-[color:var(--vscode-editor-foreground)]
  flex items-center gap-1.5
  cursor-pointer`;

const FitViewIcon = () => (
  <svg height="16" viewBox="0 0 16 16" width="16" fill="currentColor">
    <path d="M1.75 10a.75.75 0 0 1 .75.75v2.5c0 .138.112.25.25.25h2.5a.75.75 0 0 1 0 1.5h-2.5A1.75 1.75 0 0 1 1 13.25v-2.5a.75.75 0 0 1 .75-.75Zm12.5 0a.75.75 0 0 1 .75.75v2.5A1.75 1.75 0 0 1 13.25 15h-2.5a.75.75 0 0 1 0-1.5h2.5a.25.25 0 0 0 .25-.25v-2.5a.75.75 0 0 1 .75-.75ZM2.75 2.5a.25.25 0 0 0-.25.25v2.5a.75.75 0 0 1-1.5 0v-2.5C1 1.784 1.784 1 2.75 1h2.5a.75.75 0 0 1 0 1.5ZM10 1.75a.75.75 0 0 1 .75-.75h2.5c.966 0 1.75.784 1.75 1.75v2.5a.75.75 0 0 1-1.5 0v-2.5a.25.25 0 0 0-.25-.25h-2.5a.75.75 0 0 1-.75-.75Z"></path>
  </svg>
);

export function LineageControls() {
  const { updateGraph, lineageOptions } = useContext(LineageViewContext);

  const instance = useReactFlow();

  const onExpandLeft = useCallback(() => {
    updateGraph(
      {
        ...lineageOptions,
        predecessor_depth: lineageOptions.predecessor_depth + 1,
        successor_depth: lineageOptions.successor_depth,
      },
      false,
    );
  }, [lineageOptions]);

  const onExpandRight = useCallback(() => {
    updateGraph(
      {
        ...lineageOptions,
        predecessor_depth: lineageOptions.predecessor_depth,
        successor_depth: lineageOptions.successor_depth + 1,
      },
      false,
    );
  }, [lineageOptions]);

  return (
    <>
      <Panel position="bottom-left">
        <div className="flex items-center gap-1.5 justify-center">
          <div
            onClick={() => {
              instance.fitView({
                padding: 0.2,
              });
            }}
          >
            <Button
              variant="secondary"
              className="p-1 border-2 border-gray-300 hover:bg-white opacity-70 hover:opacity-100"
            >
              <Maximize className="text-muted-foreground size-5" />
            </Button>
          </div>

          <div
            onClick={() => {
              instance.zoomOut();
            }}
          >
            <Button
              variant="secondary"
              className="p-1 border-2 border-gray-300 hover:bg-white opacity-70 hover:opacity-100"
            >
              <ZoomOut className="text-muted-foreground size-5" />
            </Button>
          </div>

          <div
            onClick={() => {
              instance.zoomIn();
            }}
          >
            <Button
              variant="secondary"
              className="p-1 border-2 border-gray-300 hover:bg-white opacity-70 hover:opacity-100"
            >
              <ZoomIn className="text-muted-foreground size-5" />
            </Button>
          </div>
        </div>
      </Panel>
    </>
  );
}
