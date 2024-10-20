import CommandPanelInput from "./command-panel-input";
import CommandPanelList from "./command-panel-list";
import CommandLog from "./command-log";
import { useCommandPanelContext } from "./context";
import useResizeObserver from "use-resize-observer";

export default function CommandPanelContent({ bottomPanelHeight }: { bottomPanelHeight: number }) {
  const { commandHistory } = useCommandPanelContext();
  const { ref: headerRef, height: headerHeight } = useResizeObserver();
  const componentHeight = bottomPanelHeight - (headerHeight || 0);

  return (
    <div className="flex flex-col p-4 gap-6" style={{ height: componentHeight }}>
      <div className="flex flex-col gap-2" ref={headerRef}>
        <div>
          <p className="text-muted-foreground font-semibold">Run a dbt command</p>
          <p className="text-muted-foreground">
            Please do not refresh the page while a command is running.
          </p>
        </div>
        <CommandPanelInput />
      </div>

      <div className="flex flex-col flex-1 gap-2 min-h-0">
        <p className="text-muted-foreground font-semibold">Command History</p>
        {commandHistory.length > 0 ? (
          <div className="flex flex-1 min-h-0 gap-4">
            <div className="w-1/3 flex flex-col border-2 rounded-md overflow-y-auto">
              <CommandPanelList />
            </div>
            <div className="w-2/3 flex flex-col rounded-md border-2 p-2 overflow-y-auto">
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
