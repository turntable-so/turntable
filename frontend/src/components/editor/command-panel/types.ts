export type CommandPanelState = "idling" | "running";

export type CommandStatus = "running" | "success" | "failed" | "cancelled";

export type Command = {
    id: string;
    command: string;
    status: CommandStatus;
    time: string;
    duration?: string;
    logs?: string[];
}
