"use client";

import type { ReactNode } from "react";
import { LayoutProvider } from "@/app/contexts/LayoutContext";

export default function EditorLayout({ children }: { children: ReactNode }) {
  return (
    <LayoutProvider>
        <div className="w-full h-screen overflow-hidden">
          <div className="w-full flex-grow overflow-hidden">{children}</div>
        </div>
    </LayoutProvider>
  );
}
