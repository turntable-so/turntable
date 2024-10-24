'use client'
import TopBar from "@/components/editor/top-bar";
import { SidebarProvider } from "@/components/ui/sidebar";
import { LayoutProvider } from "@/app/contexts/LayoutContext";

export default function EditorLayout({ children }: { children: React.ReactNode }) {
    return (
        <LayoutProvider>
            <div className="w-full h-screen overflow-hidden">
                <div className="w-full flex-grow overflow-hidden">
                    {children}
                </div>
            </div>
        </LayoutProvider>
    )
}
