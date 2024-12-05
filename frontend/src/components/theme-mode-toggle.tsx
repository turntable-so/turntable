"use client";

import { useTheme } from "next-themes";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Check, SunMoon } from "lucide-react";
import { useEffect } from "react";

export function ModeToggle() {
  const { setTheme, theme } = useTheme();

  useEffect(() => {
    if (theme === "system") {
      setTheme("dark");
    }
  }, [theme]);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="flex items-center w-full">
          <SunMoon className="h-4 w-4 mr-2" />
          Theme
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" side="left">
        <DropdownMenuItem onClick={() => setTheme("light")}>
          {theme === "light" && <Check className="h-4 w-4 mr-2" />}
          Light
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>
          {theme === "dark" && <Check className="h-4 w-4 mr-2" />}
          Dark
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
