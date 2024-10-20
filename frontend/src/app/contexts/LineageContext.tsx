import { createContext, ReactNode, useContext, useState } from "react";
import { getProjectBasedLineage } from "../actions/actions";

type LineageContextType = {
    lineageData: {
        [filePath: string]: {
            data: any;
            isLoading: boolean;
        }
    };
    fetchFileBasedLineage: (filePath: string) => Promise<void>;
}

export const LineageContext = createContext<LineageContextType | undefined>(undefined);

export const LineageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [lineageData, setLineageData] = useState({});


    const fetchFileBasedLineage = async (filePath: string) => {
        setLineageData({
            ...lineageData,
            [filePath]: {
                data: null,
                isLoading: true
            }
        })
        const { lineage, root_asset } = await getProjectBasedLineage({ filePath, successor_depth: 1, predecessor_depth: 1 })
        setLineageData({
            ...lineageData,
            [filePath]: {
                data: { lineage, root_asset },
                isLoading: false
            }
        })
    }

    return (
        <LineageContext.Provider value={{ lineageData, fetchFileBasedLineage }}>
            {children}
        </LineageContext.Provider>
    )
}

export const useLineage = () => {
    const context = useContext(LineageContext);
    if (context === undefined) {
        throw new Error('useLineage must be used within a LineageProvider');
    }
    return context;
}