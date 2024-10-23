import CommandPanelContent from "./command-panel-content";
import { CommandPanelProvider } from "./command-panel-context";

export default function CommandPanelWrapper({ bottomPanelHeight }: { bottomPanelHeight: number | undefined }) {
    return (
        <CommandPanelProvider>
            <CommandPanelContent bottomPanelHeight={bottomPanelHeight} />
        </CommandPanelProvider>
    )
}