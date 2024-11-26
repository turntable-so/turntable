import { History, Plus } from "lucide-react";
import { Button } from "../../ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "../../ui/tooltip";

interface ChatHeaderProps {
  setView: (view: "chat" | "history") => void;
}

export default function ChatHeader({ setView }: ChatHeaderProps) {
  return (
    <div className="relative space-y-2 bg-muted p-1 rounded">
      <div className="flex justify-between items-center">
        <h1 className="underline underline-offset-4 uppercase font-bold text-sm">
          Chat
        </h1>
        <div className="flex items-center">
          <Tooltip delayDuration={300}>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setView("chat")}
              >
                <Plus className="w-4 h-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>New Chat</p>
            </TooltipContent>
          </Tooltip>
          <Tooltip delayDuration={300}>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setView("history")}
              >
                <History className="w-4 h-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Previous Chats</p>
            </TooltipContent>
          </Tooltip>
        </div>
      </div>
    </div>
  );
}
