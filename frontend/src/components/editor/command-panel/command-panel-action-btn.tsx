import { useEffect, useRef } from "react";
import { CircleX as CircleXIcon, Command as PlayIcon, CornerDownLeft } from "lucide-react";
import { Button } from "../../ui/button";
import { useWebSocket } from "@/app/hooks/use-websocket";
import { useCommandPanelContext } from "./context";
import getUrl from "@/app/url";
import useSession from "@/app/hooks/use-session";
import { AuthActions } from "@/lib/auth";

const baseUrl = getUrl();
const base = new URL(baseUrl).host;
const protocol = process.env.NODE_ENV === 'development' ? 'ws' : 'wss';

type CommandPanelActionBtnProps = { 
    inputValue: string;
    setInputValue: (value: string) => void;
    onRunCommand: () => void;
}

export default function CommandPanelActionBtn({ inputValue, setInputValue, onRunCommand }: CommandPanelActionBtnProps) {
    const { getToken } = AuthActions();
    const accessToken = getToken("access");
    
    const session = useSession();
    const { commandPanelState, setCommandPanelState, addCommandToHistory, updateCommandLogById, setSelectedCommandIndex, updateCommandById } = useCommandPanelContext();
    const newCommandIdRef = useRef<string | null>(null);

    
    const { startWebSocket, sendMessage } = useWebSocket(`${protocol}://${base}/ws/dbt_command/${session.user.current_workspace.id}/?token=${accessToken}`, {
        onOpen: () => {
            sendMessage(JSON.stringify({ command: inputValue }));
            setInputValue("");
        },
        onMessage: (event) => {
            console.log('Received:', event.data);
            console.log('newCommandId:', newCommandIdRef.current);
            updateCommandLogById(newCommandIdRef.current, event.data);
        },
        onError: (event) => {
            console.error('WebSocket error:', event);
            updateCommandLogById(newCommandIdRef.current, `WebSocket error: ${event}`);
            setCommandPanelState("idling");
            updateCommandById(newCommandIdRef.current, { status: "failed" });
        },
        onClose: () => {
            setCommandPanelState("idling");
            updateCommandById(newCommandIdRef.current, { status: "success", duration: `${Math.round((Date.now() - parseInt(newCommandIdRef.current)) / 1000)}s` });
        },
        timeout: 2000,
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
        onRunCommand(); // Call the onRunCommand prop
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
