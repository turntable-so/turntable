import Convert from 'ansi-to-html';
import { useCommandPanelContext } from './context';
import { Loader2 } from "lucide-react";

export default function CommandLog() {
    const { commandPanelState, commandHistory, selectedCommandIndex } = useCommandPanelContext();
    const convert = new Convert();

    const logs = commandHistory[selectedCommandIndex]?.logs || [];

    const showLoader = commandPanelState === "running" && logs.length === 0;

    return showLoader ? (
        <div className="flex items-center justify-center">
            <Loader2 className="w-6 h-6 animate-spin" />
        </div>
    ) : (
        logs.map((log, index) => (
            <p key={index} dangerouslySetInnerHTML={{ __html: convert.toHtml(log) }} />
        ))
    )
};
