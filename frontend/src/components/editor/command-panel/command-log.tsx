import React, { useState, useEffect, useRef } from "react";
import Convert from "ansi-to-html";
import { Loader2, Maximize2, X } from "lucide-react";
import { useCommandPanelContext } from "./command-panel-context";
import { Button } from "@/components/ui/button";

export default function CommandLog() {
  const { commandPanelState, commandHistory, selectedCommandIndex } =
    useCommandPanelContext();
  const convert = new Convert();

  const logs = commandHistory[selectedCommandIndex]?.logs || [];
  const showLoader = commandPanelState === "running" && logs.length === 0;
  const containerRef = useRef<HTMLDivElement | null>(null);

  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsExpanded(false);
      }
    };
    if (isExpanded) {
      document.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isExpanded]);

  const terminalContent = showLoader ? (
    <div className="flex items-center justify-center h-full">
      <Loader2 className="w-6 h-6 animate-spin" />
    </div>
  ) : (
    <div className="flex flex-col">
      {logs.map((log, index) => (
        <p
          key={index}
          dangerouslySetInnerHTML={{ __html: convert.toHtml(log) }}
          className="whitespace-pre-wrap break-words"
        />
      ))}
    </div>
  );

  if (isExpanded) {
    return (
      <div className="fixed inset-0 z-50 bg-white dark:bg-black overflow-hidden">
        <Button
          variant="ghost"
          size="icon"
          className="absolute top-0 right-0 m-2 z-10"
          onClick={() => setIsExpanded(false)}
        >
          <X className="w-4 h-4" />
        </Button>
        <div
          className="absolute inset-0 overflow-y-auto hide-scrollbar p-4"
          ref={containerRef}
        >
          {terminalContent}
        </div>
      </div>
    );
  }

  return (
    <div className="relative h-full">
      <Button
        variant="ghost"
        size="icon"
        className="absolute top-0 right-0 m-1"
        onClick={() => setIsExpanded(true)}
      >
        <Maximize2 className="w-4 h-4" />
      </Button>
      <div className="overflow-y-auto hide-scrollbar h-full" ref={containerRef}>
        {terminalContent}
      </div>
    </div>
  );
}
