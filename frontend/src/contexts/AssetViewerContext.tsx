import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { Asset } from '../types/Asset'; // Assuming you have an Asset type defined

interface AssetViewerContextType {
    assets: Asset[];
    loading: boolean;
    error: string | null;
    fetchAssets: (params?: {
        query?: string;
        source?: string;
        type?: string;
        tags?: string[];
    }) => Promise<void>;
}

const AssetViewerContext = createContext<AssetViewerContextType | undefined>(undefined);

export const useAssetViewer = () => {
    const context = useContext(AssetViewerContext);
    if (!context) {
        throw new Error('useAssetViewer must be used within an AssetViewerProvider');
    }
    return context;
};

interface AssetViewerProviderProps {
    children: ReactNode;
}

export const AssetViewerProvider: React.FC<AssetViewerProviderProps> = ({ children }) => {
    const [assets, setAssets] = useState<Asset[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchAssets = useCallback(async (params?: {
        query?: string;
        source?: string;
        type?: string;
        tags?: string[];
    }) => {
        setLoading(true);
        setError(null);
        try {
            // Replace this with your actual API call
            const response = await fetch('/api/assets', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params),
            });
            if (!response.ok) {
                throw new Error('Failed to fetch assets');
            }
            const data = await response.json();
            setAssets(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unknown error occurred');
        } finally {
            setLoading(false);
        }
    }, []);

    const value = {
        assets,
        loading,
        error,
        fetchAssets,
    };

    return (
        <AssetViewerContext.Provider value={value}>
            {children}
        </AssetViewerContext.Provider>
    );
};
