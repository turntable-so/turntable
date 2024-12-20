"use client";

import { TURNTABLE_LOCAL_STORAGE_PREFIX } from "@/app/constants/local-storage-keys";
import { useFiles } from "@/app/contexts/FilesContext";
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
  Settings,
  Sparkles,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { ModeToggle } from "../theme-mode-toggle";
import { Button } from "../ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import { Switch } from "../ui/switch";
import { Tooltip, TooltipContent, TooltipTrigger } from "../ui/tooltip";
import BranchReviewDialog from "./branch-review-dialog";

const clearTurntableCache = () => {
  const keysToRemove = [];

  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key?.startsWith(TURNTABLE_LOCAL_STORAGE_PREFIX)) {
      keysToRemove.push(key);
    }
  }

  keysToRemove.forEach((key) => localStorage.removeItem(key));
};

const EditorTopBar = () => {
  const {
    isSidebarLeftCollapsed,
    setSidebarLeftWidth,
    isBottomPanelCollapsed,
    setBottomPanelWidth,
    isSidebarRightCollapsed,
    setSidebarRightWidth,
  } = useLayoutContext();
  const router = useRouter();
  const { user, logout } = useSession();
  const {
    branchName,
    checkForProblemsOnEdit,
    setCheckForProblemsOnEdit,
    formatOnSave,
    setFormatOnSave,
  } = useFiles();
  const [branchReviewDialogOpen, setBranchReviewDialogOpen] = useState(false);

  return (
    <div
      className={cn(
        "w-full flex  bg-muted h-[52px] items-center justify-between",
        "h-[48px] px-2 pl-4 py-1 border-b border-gray-300 dark:border-zinc-700",
      )}
    >
      <div className="flex justify-center">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              onClick={() =>
                setSidebarLeftWidth(isSidebarLeftCollapsed ? 20 : 0)
              }
              variant="ghost"
              className="hover:bg-white"
              size="icon"
            >
              {isSidebarLeftCollapsed ? (
                <PanelLeftClose className="h-4 w-4" />
              ) : (
                <PanelLeft className="h-4 w-4" />
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Toggle Side Bar (⌘B)</p>
          </TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              className="hover:bg-white"
              size="icon"
              onClick={() => router.push("/projects")}
            >
              <HomeIcon className="w-4 h-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Home</p>
          </TooltipContent>
        </Tooltip>
        <Tooltip>
          <BranchReviewDialog
            open={branchReviewDialogOpen}
            onOpenChange={setBranchReviewDialogOpen}
          />
          <TooltipTrigger asChild>
            <Button
              onClick={() => setBranchReviewDialogOpen(true)}
              variant="ghost"
              className="flex items-center justify-center space-x-2 hover:bg-white"
            >
              <FolderGit2 className="w-4 h-4" />
              <div className="text-xs font-medium">
                {branchName.slice(0, 25)}
              </div>
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Version Control</p>
          </TooltipContent>
        </Tooltip>
      </div>
      <SearchBar />
      <div className=" flex justify-center items-start space-x-2">
        <Tooltip delayDuration={300}>
          <TooltipTrigger asChild>
            <Button
              onClick={() =>
                setBottomPanelWidth(isBottomPanelCollapsed ? 20 : 0)
              }
              variant="ghost"
              className="hover:bg-white"
              size="icon"
            >
              {isBottomPanelCollapsed ? (
                <PanelBottomClose className="h-4 w-4" />
              ) : (
                <PanelBottom className="h-4 w-4" />
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Toggle Bottom Panel (⌘J)</p>
          </TooltipContent>
        </Tooltip>
        <Tooltip delayDuration={300}>
          <TooltipTrigger asChild>
            <Button
              onClick={() => setSidebarRightWidth(isSidebarRightCollapsed ? 20 : 0)}
              variant="ghost"
              className="hover:bg-white"
              size="icon"
            >
              <Sparkles className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Toggle AI Chat (⌘^B)</p>
          </TooltipContent>
        </Tooltip>
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-9 hover:bg-white flex items-center space-x-1"
            >
              <Settings className="w-4 h-4" />
            </Button>
          </PopoverTrigger>
          <PopoverContent side="bottom" align="end">
            <div className="flex flex-col gap-4">
              <div className="flex gap-2 items-center justify-between">
                <div>
                  <div className="text-sm font-medium py-1">Format on save</div>
                  <div className="text-xs text-muted-foreground">
                    Format the file on save
                  </div>
                </div>
                <Switch
                  checked={formatOnSave}
                  onCheckedChange={(value) => setFormatOnSave(value)}
                />
              </div>
              <div className="flex gap-2 items-center justify-between">
                <div>
                  <div className="text-sm font-medium py-1">
                    Query validation
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Checks for problems as you type
                  </div>
                </div>
                <Switch
                  checked={checkForProblemsOnEdit}
                  onCheckedChange={(value) => setCheckForProblemsOnEdit(value)}
                />
              </div>
              <div className="flex gap-2 items-center">
                <div>
                  <div className="text-sm font-medium py-1">Clear cache</div>
                  <div className="text-xs text-muted-foreground">
                    Clears editor browser cache of saved tabs, files, and recent
                    command runs
                  </div>
                </div>
                <Button
                  onClick={() => {
                    clearTurntableCache();
                    window.location.reload();
                  }}
                  variant="secondary"
                  size="sm"
                >
                  Clear
                </Button>
              </div>
            </div>
          </PopoverContent>
        </Popover>
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
              className="flex items-center w-full"
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

export default EditorTopBar;
