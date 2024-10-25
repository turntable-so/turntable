import useSession from "@/app/hooks/use-session";
import ActionBar from "@/components/ActionBar";
import TopBar from "@/components/editor/top-bar";
import SideBar from "@/components/layout/SideBar";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import AppContextProvider from "@/contexts/AppContext";
import { cn } from "@/lib/utils";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { LayoutProvider } from "../contexts/LayoutContext";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathName = usePathname();
  const [sidebarCollapsed, collapseSidebar] = useState<boolean>(false);
  const [sidebarContext, setSidebarContext] = useState<"ACTION" | "HIDDEN">(
    "ACTION",
  );
  const [actionBarContext, setActionBarContext] = useState<
    "NOTEBOOK" | "LINEAGE"
  >("LINEAGE");

  useEffect(() => {
    collapseSidebar(
      pathName.includes("/notebooks/") ||
        pathName.includes("/lineage") ||
        pathName.includes("/sources/") ||
        pathName.includes("/assets") ||
        pathName.includes("/editor"),
    );
  }, [pathName, collapseSidebar]);

  useEffect(() => {
    if (pathName.includes("/lineage")) {
      setActionBarContext("LINEAGE");
    }
    if (pathName.includes("/notebooks")) {
      setActionBarContext("NOTEBOOK");
    }

    if (pathName.includes("/assets") || pathName.includes("/editor")) {
      setSidebarContext("HIDDEN");
    } else {
      setSidebarContext("ACTION");
    }
  }, [pathName]);

  return (
    <LayoutProvider>
      <AppContextProvider>
        <div className="h-screen">
          {/* <div
                    className={cn(
                        "w-full flex  bg-muted h-[52px] items-center justify-between",
                        "h-[48px] px-2 pl-4 py-1 border-b"
                    )}
                /> */}
          <TopBar />

          <div className="flex w-full">
            {!pathName.includes("/editor") && <SideBar />}
            <main className="flex flex-grow-1 w-full">
              {sidebarCollapsed ? (
                sidebarContext === "ACTION" ? (
                  <ResizablePanelGroup direction="horizontal" className="">
                    <ResizablePanel
                      minSize={15}
                      defaultSize={25}
                      className="w-[10px] bg-muted/50"
                    >
                      <ActionBar context={actionBarContext} />
                    </ResizablePanel>
                    <ResizableHandle />
                    <ResizablePanel defaultSize={75}>{children}</ResizablePanel>
                  </ResizablePanelGroup>
                ) : (
                  <div className="w-full h-full overflow-y-auto">
                    {children}
                  </div>
                )
              ) : (
                <div className="flex flex-col max-h-screen overflow-x-auto w-full text-muted-foreground bg-background items-center">
                  {children}
                </div>
              )}
            </main>
          </div>
        </div>
      </AppContextProvider>
    </LayoutProvider>
  );
}
