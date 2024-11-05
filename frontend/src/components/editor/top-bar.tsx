import { useLayoutContext } from "@/app/contexts/LayoutContext";
import useSession from "@/app/hooks/use-session";
import SearchBar from "@/components/editor/search-bar/search-bar";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import {
  ChevronDown,
  FolderGit2,
  HomeIcon,
  LogOut,
  PanelBottom,
  PanelBottomClose,
  PanelLeft,
  PanelLeftClose,
  PanelRight,
  PanelRightClose,
  Settings,
  Users,
} from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "../ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../ui/tooltip";
import WorkspaceSwitcher from "../workspace-switcher";
import BranchReviewDialog from "./branch-review-dialog";
import { LocalStorageKeys } from "@/app/constants/local-storage-keys";

const clearEditorCache = () => {
  localStorage.removeItem(LocalStorageKeys.activeFile);
  localStorage.removeItem(LocalStorageKeys.fileTabs);
  localStorage.removeItem(LocalStorageKeys.recentFiles);
  localStorage.removeItem(LocalStorageKeys.commandHistory);
  localStorage.removeItem(LocalStorageKeys.bottomPanelTab);
};

const AppContent = () => {
  const { appSidebarCollapsed } = useLayoutContext();
  const { user, logout } = useSession();
  return (
    <div
      className={cn(
        "w-full flex  bg-muted h-[52px] items-center justify-between",
        "h-[48px] border-b border-gray-300",
      )}
    >
      <div
        className={`flex h-[52px] w-[${appSidebarCollapsed ? "64px" : "250px"}] border-r border-gray-300  hover:bg-white hover:cursor-pointer`}
      >
        <WorkspaceSwitcher isCollapsed={appSidebarCollapsed} />
      </div>
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
