import AppContextProvider from "@/contexts/AppContext";
import { LayoutProvider } from "../contexts/LayoutContext";
import AppLayout from "./app-layout";
import { CommandPanelProvider } from "@/components/editor/command-panel/command-panel-context";

export default function WorkspaceLayout({
  children,
}: { children: React.ReactNode }) {
  return (
    <LayoutProvider>
      <AppContextProvider>
        <CommandPanelProvider>
          <AppLayout>{children}</AppLayout>
        </CommandPanelProvider>
      </AppContextProvider>
    </LayoutProvider>
  );
}
