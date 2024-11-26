import { usePathname } from "next/navigation";
import type React from "react";
import {
  type ReactNode,
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

type LayoutContextType = {
  sidebarLeftShown: boolean;
  setSidebarLeftShown: (shown: boolean) => void;
  sidebarRightShown: boolean;
  setSidebarRightShown: (shown: boolean) => void;
  bottomPanelShown: boolean;
  setBottomPanelShown: (shown: boolean) => void;
  appSidebarCollapsed: boolean;
};

const LayoutContext = createContext<LayoutContextType | undefined>(undefined);

export const useLayoutContext = () => {
  const context = useContext(LayoutContext);
  if (context === undefined) {
    throw new Error("useLayoutContext must be used within a LayoutProvider");
  }
  return context;
};

export const LayoutProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [sidebarLeftShown, setSidebarLeftShown] = useState(true);
  const [bottomPanelShown, setBottomPanelShown] = useState(true);
  // TODO: reset this back to false before merging
  const [sidebarRightShown, setSidebarRightShown] = useState(true);
  const [appSidebarCollapsed, setAppSidebarCollapsed] = useState(false);
  const pathName = usePathname();

  useEffect(() => {
    setAppSidebarCollapsed(
      pathName.includes("/lineage") || pathName.includes("/assets"),
    );
  }, [pathName]);

  const value = {
    sidebarLeftShown,
    setSidebarLeftShown,
    sidebarRightShown,
    setSidebarRightShown,
    bottomPanelShown,
    setBottomPanelShown,
    appSidebarCollapsed,
  };

  return (
    <LayoutContext.Provider value={value}>{children}</LayoutContext.Provider>
  );
};
