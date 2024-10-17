import { CircleX as CircleXIcon, Command as PlayIcon, CornerDownLeft } from "lucide-react";
import { Button } from "../../ui/button";
import { CommandPanelState } from "./types";
import { runDbtCommand } from "@/app/actions/actions";

export default function CommandPanelActionBtn({ commandPanelState, inputValue }: { commandPanelState: CommandPanelState, inputValue: string }) {

    const handleRunCommand = async () => {
        console.log("handleRunCommand: ", { inputValue })
        const response = await runDbtCommand(`dbt ${inputValue}`);
        console.log("handleRunCommand: ", { response })
    }

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
                <div className="flex flex-row gap-2 items-center"><CircleXIcon className="h-4 w-4 mr-2" />Cancel</div>
            }
        </Button>
    )
}
