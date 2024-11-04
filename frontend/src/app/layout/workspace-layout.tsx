import { LineageProvider } from "@/app/contexts/LineageContext";
import { CommandPanelProvider } from "@/components/editor/command-panel/command-panel-context";
import AppContextProvider from "@/contexts/AppContext";
import { FilesProvider } from "@/app/contexts/FilesContext";
import { LayoutProvider } from "@/app/contexts/LayoutContext";
import AppLayout from "./app-layout";
import { EditorProvider } from "@/app/contexts/EditorContext";

export default function WorkspaceLayout({
  children,
}: { children: React.ReactNode }) {
  return (
    <LayoutProvider>
      <AppContextProvider>
        <EditorProvider>
          <FilesProvider>
            <LineageProvider>
              <CommandPanelProvider>
                <AppLayout>{children}</AppLayout>
              </CommandPanelProvider>
            </LineageProvider>
          </FilesProvider>
        </EditorProvider>
      </AppContextProvider>
    </LayoutProvider>
  );
}
