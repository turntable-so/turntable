import CommandPanelContent from "./command-panel-content";
import { CommandPanelProvider } from "./context";

export default function CommandPanelWrapper({ bottomPanelHeight }: { bottomPanelHeight: number }) {
    return (
        <CommandPanelProvider>
            <CommandPanelContent bottomPanelHeight={bottomPanelHeight} />
        </CommandPanelProvider>
    )
}