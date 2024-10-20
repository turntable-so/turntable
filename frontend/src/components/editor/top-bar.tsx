import { cn } from "@/lib/utils";
import { FolderGit2, HomeIcon, PanelLeft } from "lucide-react";
import { Button } from "../ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../ui/tooltip";

export default function TopBar() {
    return (
        <TooltipProvider delayDuration={0}>
            <div
                className={cn(
                    "flex bg-muted h-[52px] items-center justify-center",
                    "h-[48px]"
                )}
            >
                <Tooltip>
                    <TooltipTrigger asChild>

                        <Button variant="ghost" className='hover:bg-white' size="icon">
                            <PanelLeft className="h-4 w-4" />
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                        <p>Toggle Side Bar (⌘B)</p>
                    </TooltipContent>
                </Tooltip>
                <Tooltip>
                    <TooltipTrigger asChild>
                        <div
                            className={cn(
                                "flex bg-muted h-[52px] items-center justify-center",
                                "h-[48px]"
                            )}
                        >
                            <Button variant="ghost" className='hover:bg-white' size="icon">
                                <HomeIcon className="w-4 h-4" />
                            </Button>
                        </div>
                    </TooltipTrigger>
                    <TooltipContent>
                        <p>Home</p>
                    </TooltipContent>
                </Tooltip>
                <Button variant='ghost' className="flex items-center justify-center">
                    <FolderGit2 className="w-4 h-4" />
                    <div className="text-muted-foreground text-sm font-medium">
                        posthog-events
                    </div>
                </Button>
            </div>
        </TooltipProvider >
    )
}   