import ActionBar from "@/components/ActionBar";
import TopBar from "@/components/editor/top-bar";
import SideBar from "@/components/layout/SideBar";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { useAppContext } from "@/contexts/AppContext";
import { usePathname } from "next/navigation";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathName = usePathname();
  const router = useRouter();
  const { focusedAsset, fetchAssetPreview } = useAppContext();
  const [sidebarCollapsed, collapseSidebar] = useState<boolean>(false);
  const [sidebarContext, setSidebarContext] = useState<"ACTION" | "HIDDEN">(
    "ACTION",
  );
  const [actionBarContext, setActionBarContext] = useState<
    "NOTEBOOK" | "LINEAGE"
  >("LINEAGE");

  const onActionBarSelectChange = (item: any) => {
    if (!item?.isSelectable) {
      return;
    }

    if (actionBarContext === "LINEAGE") {
      if (focusedAsset?.id !== item.id) {
        router.push(`/lineage/${item.id}`);
      }
    } else if (actionBarContext === "NOTEBOOK") {
      fetchAssetPreview(item.id);
    }
  };

  useEffect(() => {
    collapseSidebar(
      pathName.includes("/notebooks/") ||
        pathName.includes("/lineage") ||
        pathName.includes("/sources/") ||
        pathName.includes("/assets") ||
        pathName.includes("/editor"),
    );

    if (pathName.includes("/lineage")) {
      setActionBarContext("LINEAGE");
    } else if (pathName.includes("/notebooks")) {
      setActionBarContext("NOTEBOOK");
    }

    if (pathName.includes("/assets") || pathName.includes("/editor")) {
      setSidebarContext("HIDDEN");
    } else {
      setSidebarContext("ACTION");
    }
  }, [pathName]);

  return (
    <div className="h-screen">
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
                  <ActionBar
                    context={actionBarContext}
                    onSelectChange={onActionBarSelectChange}
                  />
                </ResizablePanel>
                <ResizableHandle />
                <ResizablePanel defaultSize={75}>{children}</ResizablePanel>
              </ResizablePanelGroup>
            ) : (
              <div className="w-full h-full overflow-y-auto">{children}</div>
            )
          ) : (
            <div className="flex flex-col max-h-screen overflow-x-auto w-full text-muted-foreground bg-muted items-center">
              {children}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
