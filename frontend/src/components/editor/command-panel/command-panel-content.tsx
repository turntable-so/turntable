import useResizeObserver from "use-resize-observer";
import CommandLog from "./command-log";
import { useCommandPanelContext } from "./command-panel-context";
import CommandPanelInput from "./command-panel-input";
import CommandPanelList from "./command-panel-list";

export default function CommandPanelContent({
  bottomPanelHeight,
}: { bottomPanelHeight: number | undefined }) {y
  const { commandHistory } = useCommandPanelContext();
  const { ref: headerRef, height: headerHeight } = useResizeObserver();
  const componentHeight = (bottomPanelHeight || 0) - (headerHeight || 0);

  return (
    <div
      className="flex flex-col p-2 gap-6"
      style={{ height: componentHeight }}
    >
      <div className="flex flex-col gap-2" ref={headerRef}>
        <CommandPanelInput />
      </div>

      <div className="flex flex-col flex-1 gap-2 min-h-0">
        {commandHistory.length > 0 ? (
          <div className="flex flex-1 min-h-0 gap-4">
            <div className="w-1/3 flex flex-col border-2 rounded-md overflow-y-auto">
              <CommandPanelList />
            </div>
            <div className="w-2/3 flex flex-col rounded-md border-2 p-2 overflow-y-auto bg-black text-white">
              <CommandLog bottomPanelHeight={componentHeight} />
            </div>
            <div className="h-12" />
          </div>
        ) : (
          <p className="text-muted-foreground">No commands run yet</p>
        )}
      </div>
    </div>
  );
}
