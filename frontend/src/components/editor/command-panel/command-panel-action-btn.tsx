import {
  CircleSlash,
  CornerDownLeft,
  Loader2,
  Play,
  Command as PlayIcon,
} from "lucide-react";
import { useEffect } from "react";
import { Button } from "../../ui/button";
import { useCommandPanelContext } from "./command-panel-context";

export default function CommandPanelActionBtn() {
  const { commandPanelState, runCommand, inputValue } =
    useCommandPanelContext();

  const componentMap = {
    idling: (
      <div className="flex flex-row gap-0.5 items-center">
        <Play className="h-4 w-4 mr-2" />
        <div className="text-xs">Run</div>
      </div>
    ),
    running: (
      <div className="flex flex-row gap-2 items-center">
        <CircleSlash className="h-4 w-4 mr-2" />
        Cancel
      </div>
    ),
    cancelling: (
      <div className="flex flex-row gap-2 items-center">
        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
        Cancelling
      </div>
    ),
  };

  const isDisabled = commandPanelState === "cancelling";


  return (
    <Button
      size="sm"
      variant="outline"
      onClick={runCommand}
      disabled={isDisabled}
    >
      {componentMap[commandPanelState]}
    </Button>
  );
}
