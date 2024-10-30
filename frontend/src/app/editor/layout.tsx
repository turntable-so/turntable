"use client";

import type { ReactNode } from "react";

export default function EditorLayout({ children }: { children: ReactNode }) {
  return (
    <div className="w-full h-screen overflow-hidden">
      <div className="w-full flex-grow overflow-hidden">{children}</div>
    </div>
  );
}
