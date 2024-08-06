import ActionBar from "@/components/ActionBar";
import SideBar from "@/components/layout/SideBar";
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from "@/components/ui/resizable";
import AppContextProvider from "@/contexts/AppContext";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import useSession from '@/app/hooks/use-session';

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
    const pathName = usePathname()
    const [sidebarCollapsed, collapseSidebar] = useState<boolean>(false)
    const [sidebarContext, setSidebarContext] = useState<'ACTION' | 'STEP'>('ACTION')
    const [actionBarContext, setActionBarContext] = useState<'NOTEBOOK' | 'LINEAGE'>('LINEAGE')

    useEffect(() => {
        collapseSidebar(
            pathName.includes('/notebooks/') ||
            pathName.includes('/lineage') ||
            pathName.includes('/sources/')
        )

        if (pathName.includes('/sources/')) {
            setSidebarContext('STEP')
        } else {
            setSidebarContext('ACTION')
        }
    }, [pathName, collapseSidebar])

    useEffect(() => {
        collapseSidebar(
            pathName.includes('/notebooks/') ||
            pathName.includes('/lineage') ||
            pathName.includes('/sources/')
        )
    }, [pathName, collapseSidebar])

    useEffect(() => {
        if (pathName.includes('/lineage')) {
            setActionBarContext('LINEAGE')
        }
        if (pathName.includes('/notebooks')) {
            setActionBarContext('NOTEBOOK')
        }
    }, [pathName])


    return (
        <AppContextProvider>
            <div className='flex h-screen'>
                <div className="flex w-full">
                    <SideBar collapsed={sidebarCollapsed} />
                    <main className="flex flex-grow-1 w-full">
                        {sidebarCollapsed ? (
                            sidebarContext === 'ACTION' ? (
                                <ResizablePanelGroup direction="horizontal" className=''>
                                    <ResizablePanel defaultSize={25} className='w-[10px] bg-muted/50'>
                                        <ActionBar context={actionBarContext} />
                                    </ResizablePanel>
                                    <ResizableHandle withHandle />
                                    <ResizablePanel defaultSize={75}>
                                        {children}
                                    </ResizablePanel>
                                </ResizablePanelGroup>
                            ) : (
                                <div className='w-full h-full overflow-y-auto'>
                                    {children}
                                </div>
                            )

                        ) : (
                            <div className='flex flex-col max-h-screen overflow-x-auto w-full text-muted-foreground bg-background items-center'>
                                {children}
                            </div>
                        )}
                    </main>
                </div >
            </div>
        </AppContextProvider>

    )
}