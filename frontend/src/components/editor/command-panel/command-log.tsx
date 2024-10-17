import { Command } from "./types";
import Convert from 'ansi-to-html';

type CommandLogProps = {
    commandHistory: Command[];
    selectedCommandIndex: number;
}

export default function CommandLog({ commandHistory, selectedCommandIndex }: CommandLogProps) {
    const convert = new Convert();

    const log = commandHistory[selectedCommandIndex]?.log || "";
    const htmlLog = convert.toHtml(log);

    return (
        <p dangerouslySetInnerHTML={{ __html: htmlLog }} />
    )
};
