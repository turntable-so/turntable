import AppContextProvider from "@/contexts/AppContext";
import { LayoutProvider } from "../contexts/LayoutContext";
import AppLayout from "./app-layout";

export default function WorkspaceLayout({
  children,
}: { children: React.ReactNode }) {
  return (
    <LayoutProvider>
      <AppContextProvider>
        <AppLayout>{children}</AppLayout>
      </AppContextProvider>
    </LayoutProvider>
  );
}
