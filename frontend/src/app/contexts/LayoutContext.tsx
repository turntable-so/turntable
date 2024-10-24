
import React, { createContext, useContext, useState, ReactNode } from 'react';

type LayoutContextType = {
    sidebarLeftShown: boolean;
    setSidebarLeftShown: (shown: boolean) => void;
    sidebarRightShown: boolean;
    setSidebarRightShown: (shown: boolean) => void;
    bottomPanelShown: boolean;
    setBottomPanelShown: (shown: boolean) => void;
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

    const value = {
        sidebarLeftShown,
        setSidebarLeftShown,
        sidebarRightShown,
        setSidebarRightShown,
        bottomPanelShown,
        setBottomPanelShown,
    };

    return <LayoutContext.Provider value={value}>{children}</LayoutContext.Provider>;
};
