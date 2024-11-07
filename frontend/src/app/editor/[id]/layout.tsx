"use client";

import type { ReactNode } from "react";

import { FilesProvider } from "@/app/contexts/FilesContext";


export default function EditorLayout({ children }: { children: ReactNode }) {
  return (
    <FilesProvider>
      <div className="w-full h-screen overflow-hidden">
        <div className="w-full flex-grow overflow-hidden">{children}</div>
      </div>
    </FilesProvider>

  );
}
