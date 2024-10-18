import CommandPanelInput from "./command-panel-input";
import CommandPanelList from "./command-panel-list";
import CommandLog from "./command-log";
import { useCommandPanelContext } from "./context";

export default function CommandPanelContent() {
  const { commandHistory } = useCommandPanelContext();

  return (
    <div className="flex flex-col h-full p-4 gap-6">
      <div className="flex flex-col gap-2">
        <p className="text-muted-foreground font-semibold">Run a dbt command</p>
        <CommandPanelInput />
      </div>

      <div className="flex flex-col gap-2 min-h-0">
        <p className="text-muted-foreground font-semibold">Command History</p>
        {commandHistory.length > 0 ? (
          <div className="flex flex-grow min-h-0 gap-4">
            <div className="w-1/3 border-2 rounded-md h-full overflow-y-auto">
              <CommandPanelList />
            </div>
            <div className="w-2/3 rounded-md border-2 p-2 h-full overflow-y-auto">
              <CommandLog />
            </div>
          </div>
        ) : (
          <p className="text-muted-foreground">No commands run yet</p>
        )}
      </div>
    </div>
  );
}
