import { cn } from "@/lib/utils";
import { ChevronDown, FolderGit2, HomeIcon, LogOut, PanelBottom, PanelBottomClose, PanelLeft, PanelLeftClose, PanelRight, PanelRightClose, Search, Users } from "lucide-react";
import { Button } from "../ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../ui/tooltip";
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import useSession from "@/app/hooks/use-session";
import { useRouter } from "next/navigation";
import { useLayoutContext } from "@/app/contexts/LayoutContext";


export default function TopBar() {
    const { user, logout } = useSession()
    const router = useRouter()
    const { sidebarLeftShown, setSidebarLeftShown, bottomPanelShown, setBottomPanelShown, sidebarRightShown, setSidebarRightShown } = useLayoutContext()
    return (
        <TooltipProvider delayDuration={0}>
            <div
                className={cn(
                    "w-full flex  bg-muted h-[52px] items-center justify-between",
                    "h-[48px] px-2 pl-4 py-1"
                )}
            >
                <div className="flex justify-center">
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Button onClick={() => setSidebarLeftShown(!sidebarLeftShown)} variant="ghost" className='hover:bg-white' size="icon">
                                {sidebarLeftShown ? <PanelLeftClose className="h-4 w-4" /> : <PanelLeft className="h-4 w-4" />}
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Toggle Side Bar (⌘B)</p>
                        </TooltipContent>
                    </Tooltip>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Button variant="ghost" className='hover:bg-white' size="icon" onClick={() => router.push('/')}>
                                <HomeIcon className="w-4 h-4" />
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Home</p>
                        </TooltipContent>
                    </Tooltip>
                    <Button variant='ghost' className="flex items-center justify-center space-x-2 hover:bg-white">
                        <FolderGit2 className="w-4 h-4" />
                        <div className="text-sm font-medium">
                            posthog-events
                        </div>
                    </Button>
                </div >
                <div className=" flex justify-center items-start space-x-2 ">
                    {/* <Button variant='ghost' size='sm' className='bg-white w-full hover:bg-gray-200 flex items-center space-x-1'>
                        <Search className='w-4 h-4' />
                        <div className="text-xs ">Search & Commands (⌘K)</div>
                    </Button> */}
                    <Button variant='ghost' size='sm' className='h-9 bg-white hover:bg-gray-200 flex items-center space-x-1'>
                        <Users className='w-4 h-4' />
                        <div className="text-xs">Invite</div>
                    </Button>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Button onClick={() => setBottomPanelShown(!bottomPanelShown)} variant="ghost" className='hover:bg-white' size="icon">
                                {bottomPanelShown ? <PanelBottomClose className="h-4 w-4" /> : <PanelBottom className="h-4 w-4" />}
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Toggle Bottom Panel (⌘J)</p>
                        </TooltipContent>
                    </Tooltip>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Button onClick={() => setSidebarRightShown(!sidebarRightShown)} variant="ghost" className='hover:bg-white' size="icon">
                                {sidebarRightShown ? <PanelRightClose className="h-4 w-4" /> : <PanelRight className="h-4 w-4" />}
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Toggle AI Chat (⌘^B)</p>
                        </TooltipContent>
                    </Tooltip>
                    <Popover>
                        <PopoverTrigger asChild className='w-full'>
                            <Button variant='ghost' size='sm' className='w-fit mr-1 h-9 flex items-center justify-end hover:bg-white space-x-1'>
                                <Avatar className='size-7 border h-7 w-7 flex items-center justify-center bg-gray-400'>
                                    <AvatarImage src={user ? user.imageUrl : ''} />
                                    <AvatarFallback className='bg-gray-400 text-white text-xs'>{user.email.slice(0, 1).toUpperCase()}</AvatarFallback>
                                </Avatar>
                                <ChevronDown className='w-3 h-3' />
                            </Button>
                        </PopoverTrigger>
                        <PopoverContent side="bottom" align="end" className='w-fit text-muted-foreground p-0'>
                            <Button onClick={logout} variant='ghost' className='flex items-center'>
                                <LogOut className='h-4 w-4 mr-2' />
                                Sign out
                            </Button>
                        </PopoverContent>
                    </Popover>

                </div>
            </div>
        </TooltipProvider >
    )
}   