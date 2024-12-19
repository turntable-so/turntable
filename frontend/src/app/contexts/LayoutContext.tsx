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
  sidebarLeftWidth: number;
  setSidebarLeftWidth: React.Dispatch<React.SetStateAction<number>>;
  sidebarRightWidth: number;
  setSidebarRightWidth: React.Dispatch<React.SetStateAction<number>>;
  bottomPanelWidth: number;
  setBottomPanelWidth: React.Dispatch<React.SetStateAction<number>>;
  appSidebarCollapsed: boolean;
  isSidebarLeftCollapsed: boolean;
  isSidebarRightCollapsed: boolean;
  isBottomPanelCollapsed: boolean;
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
  const [sidebarLeftWidth, setSidebarLeftWidth] = useState<number>(20);
  const [sidebarRightWidth, setSidebarRightWidth] = useState<number>(20);
  const [bottomPanelWidth, setBottomPanelWidth] = useState<number>(20);
  const [appSidebarCollapsed, setAppSidebarCollapsed] = useState(false);
  const pathName = usePathname();

  const isSidebarLeftCollapsed = sidebarLeftWidth === 0;
  const isSidebarRightCollapsed = sidebarRightWidth === 0;
  const isBottomPanelCollapsed = bottomPanelWidth === 0;

  useEffect(() => {
    setAppSidebarCollapsed(
      pathName.includes("/lineage") || pathName.includes("/assets"),
    );
  }, [pathName]);

  const value = {
    sidebarLeftWidth,
    setSidebarLeftWidth,
    sidebarRightWidth,
    setSidebarRightWidth,
    bottomPanelWidth,
    setBottomPanelWidth,
    appSidebarCollapsed,
    isSidebarLeftCollapsed,
    isSidebarRightCollapsed,
    isBottomPanelCollapsed,
  };

  return (
    <LayoutContext.Provider value={value}>{children}</LayoutContext.Provider>
  );
};
