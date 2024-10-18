import { CircleX as CircleXIcon, Command as PlayIcon, CornerDownLeft } from "lucide-react";
import { Button } from "../../ui/button";
import { Command, CommandPanelState } from "./types";
import { useWebSocket } from "@/app/hooks/use-websocket";
import { useEffect, useRef } from "react";

type CommandPanelActionBtnProps = { 
    commandPanelState: CommandPanelState;
    inputValue: string;
    setCommandPanelState: (state: CommandPanelState) => void;
    addCommandToHistory: (newCommand: Command) => void;
    updateCommandLogById: (id: string, newLog: string) => void;
    setSelectedCommandIndex: (index: number) => void;
}

export default function CommandPanelActionBtn({ commandPanelState, inputValue, setCommandPanelState, addCommandToHistory, updateCommandLogById, setSelectedCommandIndex }: CommandPanelActionBtnProps) {
    const newCommandIdRef = useRef<string | null>(null);
    
    // TODO: make this dynamic
    const { startWebSocket, sendMessage } = useWebSocket('ws://localhost:8000/ws/dbt_command/1/', {
        onOpen: () => {
            sendMessage(JSON.stringify({ command: inputValue }));
        },
        onMessage: (event) => {
            console.log('Received:', event.data);
            const message = JSON.parse(event.data) as { event: "update"; payload: string; };
            console.log('newCommandId:', newCommandIdRef.current);
            updateCommandLogById(newCommandIdRef.current, message.payload);
        },
        onError: (event) => {
            console.error('WebSocket error:', event);
            updateCommandLogById(newCommandIdRef.current, `WebSocket error: ${event}`);
            setCommandPanelState("idling");
        },
        onClose: () => {
            setCommandPanelState("idling");
        }
    });

    const handleRunCommand = () => {
        if (!inputValue || commandPanelState === "running") {
            return;
        }

        console.log('handleRunCommand:', { inputValue });
        startWebSocket();
        setCommandPanelState("running");

        const commandId = Date.now().toString();
        newCommandIdRef.current = commandId;
        addCommandToHistory({
            id: commandId,
            command: inputValue,
            status: "running",
            time: new Date().toLocaleTimeString()
        });
        setSelectedCommandIndex(0);
    };

    const handleCommandEnterShortcut = () => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
                event.preventDefault();
                handleRunCommand();
            }
        };

        window.addEventListener('keydown', handleKeyDown);

        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }
    useEffect(handleCommandEnterShortcut, [inputValue]);

    return (
        <Button size='sm'
            variant="outline"
            onClick={handleRunCommand}
        >
            {
                commandPanelState === "idling" ? 
                <div className="flex flex-row gap-0.5 items-center mr-2 text-base">
                    <PlayIcon className="h-4 w-4 mr-0.5" />
                    <CornerDownLeft className="h-4 w-4 mr-2" /> Run
                </div> :
                <div className="flex flex-row gap-2 items-center">
                    <CircleXIcon className="h-4 w-4 mr-2" />
                    Cancel
                </div>
            }
        </Button>
    )
}
