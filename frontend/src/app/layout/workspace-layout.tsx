import { CommandPanelProvider } from "@/components/editor/command-panel/command-panel-context";
import AppContextProvider from "@/contexts/AppContext";
import { FilesProvider } from "@/app/contexts/FilesContext";
import { LayoutProvider } from "@/app/contexts/LayoutContext";
import AppLayout from "./app-layout";
import { LineageViewProvider } from "@/app/contexts/LineageView";

export default function WorkspaceLayout({
  children,
}: { children: React.ReactNode }) {
  return (
    <LayoutProvider>
      <AppContextProvider>
        <FilesProvider>
          <LineageViewProvider>
            <CommandPanelProvider>
              <AppLayout>{children}</AppLayout>
            </CommandPanelProvider>
          </LineageViewProvider>
        </FilesProvider>
      </AppContextProvider>
    </LayoutProvider>
  );
}
