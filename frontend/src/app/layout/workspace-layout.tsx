import { LineageProvider } from "@/app/contexts/LineageContext";
import { CommandPanelProvider } from "@/components/editor/command-panel/command-panel-context";
import AppContextProvider from "@/contexts/AppContext";
import { FilesProvider } from "../contexts/FilesContext";
import { LayoutProvider } from "../contexts/LayoutContext";
import AppLayout from "./app-layout";

export default function WorkspaceLayout({
  children,
}: { children: React.ReactNode }) {
  return (
    <LayoutProvider>
      <AppContextProvider>
        <LayoutProvider>
          <FilesProvider>
            <LineageProvider>
              <CommandPanelProvider>
                <AppLayout>{children}</AppLayout>
              </CommandPanelProvider>
            </LineageProvider>
          </FilesProvider>
        </LayoutProvider>
      </AppContextProvider>
    </LayoutProvider>
  );
}
