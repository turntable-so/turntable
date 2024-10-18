import CommandPanelContent from "./command-panel-content";
import { CommandPanelProvider } from "./context";

export default function CommandPanelWrapper() {
    return (
        <CommandPanelProvider>
            <CommandPanelContent />
        </CommandPanelProvider>
    )
}