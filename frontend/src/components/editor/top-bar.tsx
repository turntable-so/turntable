import { useLayoutContext } from "@/app/contexts/LayoutContext";
import useSession from "@/app/hooks/use-session";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import { ChevronDown, LogOut } from "lucide-react";
import { usePathname } from "next/navigation";
import { Button } from "../ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import { TooltipProvider } from "../ui/tooltip";
import WorkspaceSwitcher from "../workspace-switcher";
import { ModeToggle } from "../theme-mode-toggle";

const AppContent = () => {
  const { appSidebarCollapsed } = useLayoutContext();
  const { user, logout } = useSession();
  return (
    <div
      className={cn(
        "w-full flex bg-muted h-[52px] items-center justify-between",
        "h-[48px] border-b border-gray-300 dark:border-gray-950",
      )}
    >
      <div
        className={`flex h-[52px] w-[${appSidebarCollapsed ? "64px" : "250px"}] border-r border-gray-300 dark:border-gray-950 dark:hover:bg-black hover:bg-white hover:cursor-pointer`}
      >
        <WorkspaceSwitcher isCollapsed={appSidebarCollapsed} />
      </div>
      <div className="flex items-center space-x-1">
        <Popover>
          <PopoverTrigger asChild className="w-full">
            <Button
              variant="ghost"
              size="sm"
              className="w-fit mr-1 h-9 flex items-center justify-end hover:bg-white space-x-1"
            >
              <Avatar className="size-7 border h-7 w-7 flex items-center justify-center bg-gray-400">
                <AvatarImage src={user ? user.imageUrl : ""} />
                <AvatarFallback className="bg-gray-400 text-white text-xs">
                  {user.email.slice(0, 1).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <ChevronDown className="w-3 h-3" />
            </Button>
          </PopoverTrigger>
          <PopoverContent
            side="bottom"
            align="end"
            className="w-fit text-muted-foreground p-0"
          >
            <ModeToggle />
            <Button
              onClick={logout}
              variant="ghost"
              className="flex items-center"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Sign out
            </Button>
          </PopoverContent>
        </Popover>
      </div>
    </div>
  );
};

export default function TopBar() {
  const pathname = usePathname();
  return (
    <TooltipProvider delayDuration={0}>
      {pathname.includes("/editor") ? null : <AppContent />}
    </TooltipProvider>
  );
}
