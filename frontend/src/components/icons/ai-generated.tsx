import React from "react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../ui/tooltip";
import Magic from "./magic";

export default function AiGenerated() {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger>
          <Magic className="w-5 h-5 col-span-1" />
        </TooltipTrigger>
        <TooltipContent>AI Generated</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};
