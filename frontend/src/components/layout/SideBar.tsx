"use client";

import { Button } from "@/components/ui/button";
import {
  Boxes,
  DatabaseZap,
  FolderGit2,
  Network,
  Settings,
  Users,
  Workflow,
} from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useLayoutContext } from "@/app/contexts/LayoutContext";
import { cn } from "@/lib/utils";
import { TooltipProvider } from "../ui/tooltip";

const links = [
  {
    title: "Connections",
    icon: DatabaseZap,
    variant: "ghost",
    link: "/connections",
  },
  {
    title: "Assets",
    icon: Boxes,
    variant: "ghost",
    link: "/assets",
  },
  {
    title: "Projects",
    icon: FolderGit2,
    variant: "ghost",
    link: "/projects",
  },
  // {
  //   title: "Jobs",
  //   icon: Workflow,
  //   variant: "ghost",
  //   link: "/jobs",
  // },
  {
    title: "Lineage",
    icon: Network,
    variant: "ghost",
    link: "/lineage",
  },
  {
    title: "Workspace",
    icon: Users,
    variant: "ghost",
    link: "/team",
  },
  {
    title: "Settings",
    icon: Settings,
    variant: "ghost",
    link: "/settings",
  },
];

export default function SideBar() {
  const pathName = usePathname();
  const router = useRouter();
  const { appSidebarCollapsed } = useLayoutContext();

  return (
    <div
      className={cn(
        "flex-shrink-0 bg-muted",
        appSidebarCollapsed ? "w-[64px]" : "w-[250px]",
        "border-r border-gray-300 dark:border-gray-950",
      )}
    >
      <TooltipProvider delayDuration={0}>
        <div className="flex flex-col justify-between h-screen text-muted-foreground">
          <div className="flex flex-col gap-2 mt-4">
            {links.map((link: any) =>
              appSidebarCollapsed ? (
                <Button
                  onClick={() => router.push(link.link)}
                  variant="ghost"
                  key={link.title}
                  className={`flex  items-center justify-center hover:bg-white dark:hover:bg-black ${pathName.includes(link.link) ? "bg-white dark:bg-black" : ""}`}
                >
                  <link.icon className="h-4 w-4" />
                </Button>
              ) : (
                <Button
                  onClick={() => router.push(link.link)}
                  variant="ghost"
                  key={link.title}
                  className={`mx-2 px-4 flex items-center justify-start hover:bg-white dark:hover:bg-black ${pathName.includes(link.link) ? "bg-white dark:bg-black" : ""}`}
                >
                  <link.icon className="h-4 w-4 mr-2" />
                  {link.title}
                </Button>
              ),
            )}
          </div>
        </div>
      </TooltipProvider>
    </div>
  );
}
