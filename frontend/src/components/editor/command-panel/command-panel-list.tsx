import React, { useEffect, useState } from "react";
import {
  CircleCheck,
  CircleSlash,
  CircleX,
  LoaderCircle,
  Play,
} from "lucide-react";
import { useCommandPanelContext } from "./command-panel-context";

export default function CommandPanelList() {
  const {
    commandHistory,
    selectedCommandIndex,
    setSelectedCommandIndex,
    commandPanelState,
    updateCommandById,
    runCommandCore,
  } = useCommandPanelContext();

  const [hoveredButtonIndex, setHoveredButtonIndex] = useState<number | null>(
    null,
  );

  useEffect(() => {
    commandHistory.forEach((command) => {
      if (command.status === "running" && commandPanelState === "idling") {
        updateCommandById(command.id, { status: "cancelled" });
      }
    });
  }, [commandHistory]);

  return (
    <div className="flex flex-col">
      {commandHistory.map((item, index) => (
        <div
          key={item.id}
          className={`group/item flex justify-between ${
            index === selectedCommandIndex && hoveredButtonIndex !== index
              ? "bg-zinc-200 dark:bg-zinc-700"
              : ""
          } ${
            hoveredButtonIndex !== index
              ? "hover:bg-zinc-200 dark:hover:bg-zinc-700"
              : ""
          } cursor-pointer p-2`}
          onClick={() => setSelectedCommandIndex(index)}
        >
          <div
            className={`flex flex-row gap-2 items-center ${
              item.status === "failed" ? "text-red-600" : ""
            }`}
          >
            {item.status === "running" && (
              <LoaderCircle className="h-4 w-4 flex-shrink-0 animate-spin" />
            )}
            {item.status === "success" && (
              <CircleCheck className="h-4 w-4 flex-shrink-0" />
            )}
            {item.status === "failed" && (
              <CircleX className="h-4 w-4 flex-shrink-0" />
            )}
            {item.status === "cancelled" && (
              <CircleSlash className="h-4 w-4 flex-shrink-0" />
            )}
            <p>dbt {item.command}</p>
          </div>
          <div className="flex items-center">
            {item.duration && (
              <p className="group-hover/item:hidden">{item.duration}</p>
            )}
            <div className="hidden group-hover/item:block">
              <button
                type="button"
                className="group/run flex items-center gap-1 rounded hover:bg-gray-200 dark:hover:bg-zinc-700 text-sm px-2"
                onMouseEnter={() => setHoveredButtonIndex(index)}
                onMouseLeave={() => setHoveredButtonIndex(null)}
                onClick={(e) => {
                  e.stopPropagation();
                  runCommandCore(item.command);
                }}
              >
                <Play className="h-3 w-3" />
                <span>Run</span>
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
