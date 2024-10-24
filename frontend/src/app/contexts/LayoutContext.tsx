
import { usePathname } from 'next/navigation';
import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';

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
        throw new Error('useLayoutContext must be used within a LayoutProvider');
    }
    return context;
};

export const LayoutProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [sidebarLeftShown, setSidebarLeftShown] = useState(true);
    const [bottomPanelShown, setBottomPanelShown] = useState(true);
    const [sidebarRightShown, setSidebarRightShown] = useState(false);
    const [appSidebarCollapsed, setAppSidebarCollapsed] = useState(false);
    const pathName = usePathname()

    console.log({ sidebarLeftShown, sidebarRightShown, bottomPanelShown })

    useEffect(() => {
        setAppSidebarCollapsed(
            pathName.includes('/lineage') ||
            pathName.includes('/assets')
        )
    }, [pathName])




    const value = {
        sidebarLeftShown,
        setSidebarLeftShown,
        sidebarRightShown,
        setSidebarRightShown,
        bottomPanelShown,
        setBottomPanelShown,
        appSidebarCollapsed,
    };

    return <LayoutContext.Provider value={value}>{children}</LayoutContext.Provider>;
};
