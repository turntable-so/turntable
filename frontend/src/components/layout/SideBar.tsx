"use client";
import useSession from "@/app/hooks/use-session";
import { Nav } from "@/components/nav";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  BookOpen,
  Boxes,
  Code,
  Database,
  DatabaseZap,
  FileBarChart,
  FolderGit2,
  LogOut,
  Network,
  Settings,
  Users,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { SearchDialog } from "../SearchDialog";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";

import { useLayoutContext } from "@/app/contexts/LayoutContext";
import { cn } from "@/lib/utils";
import {
  AlertCircle,
  Archive,
  ArchiveX,
  File,
  Inbox,
  MessagesSquare,
  Search,
  Send,
  ShoppingCart,
  Trash2,
  Users2,
} from "lucide-react";
import { TooltipProvider } from "../ui/tooltip";

export const accounts = [
  {
    label: "Alicia Koch",
    email: "alicia@example.com",
    icon: (
      <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <title>Vercel</title>
        <path d="M24 22.525H0l12-21.05 12 21.05z" fill="currentColor" />
      </svg>
    ),
  },
  {
    label: "Alicia Koch",
    email: "alicia@gmail.com",
    icon: (
      <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <title>Gmail</title>
        <path
          d="M24 5.457v13.909c0 .904-.732 1.636-1.636 1.636h-3.819V11.73L12 16.64l-6.545-4.91v9.273H1.636A1.636 1.636 0 0 1 0 19.366V5.457c0-2.023 2.309-3.178 3.927-1.964L5.455 4.64 12 9.548l6.545-4.91 1.528-1.145C21.69 2.28 24 3.434 24 5.457z"
          fill="currentColor"
        />
      </svg>
    ),
  },
  {
    label: "Alicia Koch",
    email: "alicia@me.com",
    icon: (
      <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <title>iCloud</title>
        <path
          d="M13.762 4.29a6.51 6.51 0 0 0-5.669 3.332 3.571 3.571 0 0 0-1.558-.36 3.571 3.571 0 0 0-3.516 3A4.918 4.918 0 0 0 0 14.796a4.918 4.918 0 0 0 4.92 4.914 4.93 4.93 0 0 0 .617-.045h14.42c2.305-.272 4.041-2.258 4.043-4.589v-.009a4.594 4.594 0 0 0-3.727-4.508 6.51 6.51 0 0 0-6.511-6.27z"
          fill="currentColor"
        />
      </svg>
    ),
  },
];

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
        "border-r border-gray-300",
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
                  className={`flex  items-center justify-center  hover:bg-white ${pathName.includes(link.link) ? "bg-white" : ""}`}
                >
                  <link.icon className="h-4 w-4" />
                </Button>
              ) : (
                <Button
                  onClick={() => router.push(link.link)}
                  variant="ghost"
                  key={link.title}
                  className={`mx-2 px-4 flex items-center justify-start  hover:bg-white ${pathName.includes(link.link) ? "bg-white" : ""}`}
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
