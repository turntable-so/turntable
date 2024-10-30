import { CommandPanelProvider } from "@/components/editor/command-panel/command-panel-context";
import AppContextProvider from "@/contexts/AppContext";
import { LayoutProvider } from "../contexts/LayoutContext";
import AppLayout from "./app-layout";
import { FilesProvider } from "../contexts/FilesContext";
import {LineageProvider} from "@/app/contexts/LineageContext";

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
