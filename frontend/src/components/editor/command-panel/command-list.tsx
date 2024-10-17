import { CircleCheck, CircleX, LoaderCircle } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Command } from "./types";

type CommandListProps = {
  commandHistory: Command[];
  selectedCommandIndex: number;
  setSelectedCommandIndex: (index: number) => void;
}

export default function CommandList({ commandHistory, selectedCommandIndex, setSelectedCommandIndex }: CommandListProps) {
    return (
        <ScrollArea>
            {commandHistory.map((item, index) => (
                <div key={item.id} className={`flex justify-between ${index === selectedCommandIndex ? 'bg-gray-100' : ''} hover:bg-gray-100 cursor-pointer p-2`} onClick={() => setSelectedCommandIndex(index)}>
                    <div className={`flex flex-row gap-2 items-center ${item.status === 'failed' ? 'text-red-600' : ''}`}>
                        {item.status === 'running' && <LoaderCircle className="h-4 w-4 animate-spin" />}
                        {item.status === 'success' && <CircleCheck className="h-4 w-4" />}
                        {item.status === 'failed' && <CircleX className="h-4 w-4" />}
                        <p>{item.command}</p>
                    </div>
                    <div className="flex flex-row gap-2 items-center">
                        {item.duration && <p>{item.duration}</p>}
                        <p>{item.time}</p>
                    </div>
                </div>
            ))}
        </ScrollArea>
    )
}