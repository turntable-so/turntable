import useResizeObserver from "use-resize-observer";
import CommandLog from "./command-log";
import { useCommandPanelContext } from "./command-panel-context";
import CommandPanelInput from "./command-panel-input";
import CommandPanelList from "./command-panel-list";

export default function CommandPanelContent({
  bottomPanelHeight,
}: { bottomPanelHeight: number | undefined }) {
  const { commandHistory } = useCommandPanelContext();
  const componentHeight = (bottomPanelHeight || 0) - 48;

  return (
    <div
      className="flex flex-col p-4 gap-4"
      style={{ height: componentHeight }}
    >
      <CommandPanelInput />

      <div className="flex flex-col flex-1 gap-2 min-h-0">
        {commandHistory.length > 0 ? (
          <div className="flex flex-1 min-h-0 gap-4">
            <div className="w-1/3 flex flex-col border-2 rounded-md overflow-y-auto">
              <CommandPanelList />
            </div>
            <div className="w-2/3 flex flex-col rounded-md border-2 p-2 overflow-y-auto bg-black text-white">
              <CommandLog bottomPanelHeight={componentHeight} />
            </div>
          </div>
        ) : (
          <p className="text-muted-foreground">No commands run yet</p>
        )}
      </div>
    </div>
  );
}
