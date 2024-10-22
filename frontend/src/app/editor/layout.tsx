'use client'
import TopBar from "@/components/editor/top-bar";
import { SidebarProvider } from "@/components/ui/sidebar";

export default function EditorLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="w-full h-screen overflow-hidden">
            <TopBar />
            <div className="w-full flex-grow overflow-hidden">
                {children}
            </div>
        </div>
    )
}
