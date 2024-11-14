import { Minus, Plus } from "lucide-react";
import { useContext } from "react";
import { Panel } from "@xyflow/react";
import { Button } from "../ui/button";
import { LineageViewContext } from "./LineageView";

export default function LineageOptions() {
  const {
    rootAsset,
    lineageOptions,
    setIsLineageOptionsPanelOpen,
    isLineageOptionsPanelOpen,
    setLineageOptionsAndRefetch,
  } = useContext(LineageViewContext);

  if (!rootAsset || !lineageOptions) return null;

  const incrementPredecessorDepth = (delta: number) => {
    if (lineageOptions.predecessor_depth + delta < 1) return;
    if (lineageOptions.predecessor_depth + delta > 5) return;
    setLineageOptionsAndRefetch({
      ...lineageOptions,
      predecessor_depth: lineageOptions.predecessor_depth + delta,
    });
  };
  const incrementSuccessorDepth = (delta: number) => {
    if (lineageOptions.successor_depth + delta < 1) return;
    if (lineageOptions.successor_depth + delta > 5) return;
    setLineageOptionsAndRefetch({
      ...lineageOptions,
      successor_depth: lineageOptions.successor_depth + delta,
    });
  };

  return (
    <Panel position="top-left">
      {isLineageOptionsPanelOpen ? (
        <div
          onClick={() => setIsLineageOptionsPanelOpen(true)}
          className="px-3 p-2 text-sm font-medium text-muted-foreground border-2 border-card bg-card rounded-md"
        >
          <div className="flex space-x-2 text-muted-foreground items-center">
            <div className="flex flex-col items-center space-y-1">
              <Button
                onClick={() => incrementPredecessorDepth(1)}
                variant="secondary"
                className="p-0 h-5 opacity-70 hover:opacity-100"
              >
                <Plus className="size-4" />
              </Button>
              <div className="py-0.5">{lineageOptions.predecessor_depth}</div>
              <Button
                onClick={() => incrementPredecessorDepth(-1)}
                variant="secondary"
                className="p-0 h-5 opacity-70 hover:opacity-100"
              >
                <Minus className="size-4" />
              </Button>
            </div>
            <div>{rootAsset.name}</div>
            <div className="flex flex-col items-center space-y-1">
              <Button
                onClick={() => incrementSuccessorDepth(1)}
                variant="secondary"
                className="p-0 h-5 opacity-70 hover:opacity-100"
              >
                <Plus className="size-4" />
              </Button>
              <div className="py-0.5">{lineageOptions.successor_depth}</div>
              <Button
                onClick={() => incrementSuccessorDepth(-1)}
                variant="secondary"
                className="p-0 h-5 opacity-70 hover:opacity-100"
              >
                <Minus className="size-4" />
              </Button>
            </div>
          </div>
        </div>
      ) : (
        <div
          onClick={() => setIsLineageOptionsPanelOpen(true)}
          className=" cursor-pointer opacity-70 hover:opacity-100 px-3 p-2 text-sm font-medium text-muted-foreground border-2 border-card bg-card rounded-md"
        >
          <div className="flex space-x-2 items-center">
            <div className="bg-muted text-xs font-bold p-1 rounded-full w-4 h-4 flex items-center justify-center">
              {lineageOptions.predecessor_depth}
            </div>
            <div>+{rootAsset.name}+</div>
            <div className="bg-muted text-xs font-bold p-1 rounded-full w-4 h-4 flex items-center justify-center">
              {lineageOptions.successor_depth}
            </div>
          </div>
        </div>
      )}
    </Panel>
  );
}
