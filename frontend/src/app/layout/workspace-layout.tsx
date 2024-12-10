import { FilesProvider } from "@/app/contexts/FilesContext";
import { LayoutProvider } from "@/app/contexts/LayoutContext";
import { LineageViewProvider } from "@/app/contexts/LineageView";
import { AISidebarProvider } from "@/components/editor/ai/ai-sidebar-context";
import { CommandPanelProvider } from "@/components/editor/command-panel/command-panel-context";
import AppContextProvider from "@/contexts/AppContext";
import AppLayout from "./app-layout";

export default function WorkspaceLayout({
  children,
}: { children: React.ReactNode }) {
  return (
    <LayoutProvider>
      <AppContextProvider>
        <FilesProvider>
          <LineageViewProvider>
            <CommandPanelProvider>
              <AISidebarProvider>
                <AppLayout>{children}</AppLayout>
              </AISidebarProvider>
            </CommandPanelProvider>
          </LineageViewProvider>
        </FilesProvider>
      </AppContextProvider>
    </LayoutProvider>
  );
}
