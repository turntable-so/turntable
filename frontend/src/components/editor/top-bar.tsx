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
  Search,
  Settings,
} from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useState, useEffect } from "react";
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
import { useAssets } from "@/contexts/AssetViewerContext";
import { Input } from "../ui/input";

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

  const { query, setQuery, assets, submitSearch } =
    useAssets();

  useEffect(() => {
    submitSearch();
  }, []);


  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      submitSearch();
    }
  };



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
      <div className="flex flex-row justify-between w-full items-center">
      <div className="flex items-center">
              <div className="relative w-full">
                <Search className="size-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  autoFocus
                  placeholder="Search assets"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  onKeyDown={handleKeyDown}
                  className="h-10 w-full pl-10"
                />
              </div>
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
      {/* Add search bar here */}
    </div>
  );
};
const EditorContent = () => {
  const {
    sidebarLeftShown,
    setSidebarLeftShown,
    bottomPanelShown,
    setBottomPanelShown,
    sidebarRightShown,
    setSidebarRightShown,
  } = useLayoutContext();
  const router = useRouter();
  const { user, logout } = useSession();
  const [branchReviewDialogOpen, setBranchReviewDialogOpen] = useState(false);

  return (
    <div
      className={cn(
        "w-full flex  bg-muted h-[52px] items-center justify-between",
        "h-[48px] px-2 pl-4 py-1 border-b border-gray-300",
      )}
    >
      <div className="flex justify-center">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              onClick={() => setSidebarLeftShown(!sidebarLeftShown)}
              variant="ghost"
              className="hover:bg-white"
              size="icon"
            >
              {sidebarLeftShown ? (
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
        <BranchReviewDialog
          open={branchReviewDialogOpen}
          onOpenChange={setBranchReviewDialogOpen}
        />
        <Button
          onClick={() => setBranchReviewDialogOpen(true)}
          variant="ghost"
          className="flex items-center justify-center space-x-2 hover:bg-white"
        >
          <FolderGit2 className="w-4 h-4" />
          <div className="text-sm font-medium">posthog-events</div>
        </Button>
      </div>
      <SearchBar />
      <div className=" flex justify-center items-start space-x-2 ">
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="h-9 bg-white hover:bg-gray-200 flex items-center space-x-1"
            >
              <Settings className="w-4 h-4" />
              <div className="text-xs">Settings</div>
            </Button>
          </PopoverTrigger>
          <PopoverContent
            side="bottom"
            align="end"
            className="w-fit text-muted-foreground p-0"
          >
            <Button
              variant="ghost"
              className="flex items-center"
              onClick={() => {
                clearEditorCache();
              }}
            >
              Clear Editor Cache
            </Button>
          </PopoverContent>
        </Popover>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              onClick={() => setBottomPanelShown(!bottomPanelShown)}
              variant="ghost"
              className="hover:bg-white"
              size="icon"
            >
              {bottomPanelShown ? (
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
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              onClick={() => setSidebarRightShown(!sidebarRightShown)}
              variant="ghost"
              className="hover:bg-white"
              size="icon"
            >
              {sidebarRightShown ? (
                <PanelRightClose className="h-4 w-4" />
              ) : (
                <PanelRight className="h-4 w-4" />
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Toggle AI Chat (⌘^B)</p>
          </TooltipContent>
        </Tooltip>
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
    </div>
  );
};

export default function TopBar() {
  const pathname = usePathname();
  return (
    <TooltipProvider delayDuration={0}>
      {pathname.includes("/editor") ? <EditorContent /> : <AppContent />}
    </TooltipProvider>
  );
}
