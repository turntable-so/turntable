"use client";
import { Button } from "./ui/button";
import { Separator } from "./ui/separator";

import { Plus } from "lucide-react";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { type Block, useAppContext } from "../contexts/AppContext";
import PromptBlock from "./PromptBlock";
import QueryBlock from "./QueryBlock";
import { Card, CardContent } from "./ui/card";

const AutoExpandTextarea = () => {
  const [text, setText] = useState("");

  const handleChange = (event: any) => {
    const textarea = event.target;
    // Reset the height to auto (to shrink if necessary)
    textarea.style.height = "auto";
    // Set the height to scrollHeight to expand the textarea
    textarea.style.height = `${textarea.scrollHeight}px`;
    setText(textarea.value);
  };

  return (
    <Card>
      <CardContent className="p-4 bg-muted">
        <textarea
          className="w-full bg-transparent resize-none focus:ring-0 focus:outline-none"
          value={text}
          onChange={handleChange}
        />
      </CardContent>
    </Card>
  );
};

type Notebook = {
  id: string;
  title: string;
  blocks: Block[];
};

export default function Notebook({ notebook }: { notebook: Notebook }) {
  const {
    activeNotebook,
    onSqlChange,
    runQuery,
    addPromptBlock,
    setActiveNotebook,
  } = useAppContext();
  const [maxWidth, setMaxWidth] = useState<number>(0);
  const divRef = useRef(null);
  const [blocks, setBlocks] = useState<[]>([]);

  const pathName = usePathname();

  useEffect(() => {
    setActiveNotebook(notebook);
  }, [notebook]);

  function calculateDistances() {
    if (divRef.current) {
      // @ts-ignore
      const rect = divRef.current.getBoundingClientRect();
      const viewportWidth = window.innerWidth;

      const divWidthBasedOnPosition = viewportWidth - rect.left - 50;
      // padding on each side
      setMaxWidth(divWidthBasedOnPosition);
    }
  }

  useEffect(() => {
    // Initial calculation
    calculateDistances();

    // Set up resize event listener
    window.addEventListener("resize", calculateDistances);

    // Clean up
    return () => window.removeEventListener("resize", calculateDistances);
  }, []); // Empty dependency array means this runs once on mount and cleanup on unmount

  if (!activeNotebook) {
    return null;
  }

  return (
    <div style={{}} ref={divRef} className="p-2 mt-12 px-8 ">
      <div
        style={{
          maxWidth: `${maxWidth}px`,
        }}
        className=""
      >
        <input
          onChange={(e) =>
            setActiveNotebook({ ...activeNotebook, title: e.target.value })
          }
          className="w-full  border-transparent focus:outline-none focus:border-transparent focus:ring-0 scroll-m-20 text-3xl bg-transparent font-medium tracking-tight"
          value={activeNotebook.title}
        />
        <div className="mt-12">
          <div className="h-12" />
          <div className="space-y-16">
            {activeNotebook.blocks.map((block: Block, i: number) => {
              if (block.type === "query") {
                return (
                  <QueryBlock
                    // @ts-ignore
                    onRunQueryClick={() => runQuery(block.id)}
                    database={block.database}
                    // @ts-ignore
                    title={block.title}
                    key={block.id}
                    onSqlChange={(sql: string) => onSqlChange(block.id, sql)}
                    sql={block.sql}
                    records={block.records}
                  />
                );
              }
              if (block.type === "prompt") {
                return <PromptBlock key={i} />;
              }
              return <div key={i}>Unknown block type</div>;
            })}
          </div>
        </div>
        <div className="mt-16">
          <div className="flex items-center space-x-4 opacity-60 hover:opacity-100">
            <Separator />
            <Button onClick={addPromptBlock} variant="secondary">
              <Plus className="w-4 h-4 text-gray-400" />
            </Button>
            <Separator />
          </div>
        </div>
        <div className="h-24" />
      </div>
    </div>
  );
}
