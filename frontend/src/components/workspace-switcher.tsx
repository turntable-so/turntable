"use client";

import * as React from "react";

import useSession from "@/app/hooks/use-session";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { Avatar } from "@radix-ui/react-avatar";
import { ChevronDown } from "lucide-react";
import { useRouter } from "next/navigation";
import { AvatarFallback, AvatarImage } from "./ui/avatar";

interface AccountSwitcherProps {
  isCollapsed: boolean;
}

export default function WorkspaceSwitcher({
  isCollapsed,
}: AccountSwitcherProps) {
  const { user } = useSession();
  const { current_workspace } = user;
  const router = useRouter();
  return (
    <div
      className={`w-full flex items-center px-4  gap-1 text-muted-foreground font-medium justify-between ${!isCollapsed ? "ml-1" : ""}`}
      onClick={() => router.push("/workspaces")}
    >
      <div className="flex items-center">
        <Avatar
          className={`border ${isCollapsed ? "h-8 w-8" : "h-7 w-7"} flex items-center justify-center bg-gray-400 dark:bg-gray-700 rounded-sm`}
        >
          <AvatarImage src={current_workspace?.icon_url} />
          <AvatarFallback className="text-white font-bold bg-gray-400 dark:bg-gray-700">
            {current_workspace?.name.slice(0, 1).toUpperCase()}
          </AvatarFallback>
        </Avatar>
        <div className="flex items-center text-sm">
          {!isCollapsed && (
            <span className="ml-2">{current_workspace?.name}</span>
          )}
        </div>
      </div>
      <ChevronDown className="w-4 h-4" />
    </div>
  );
}
