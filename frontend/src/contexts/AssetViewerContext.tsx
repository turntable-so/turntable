import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { Asset } from '../types/Asset'; // Assuming you have an Asset type defined
import { getAssets } from '@/app/actions/actions';

interface AssetViewerContextType {
    assets: AssetView;
    loading: boolean;
    error: string | null;
    fetchAssets: (params?: {
        query?: string;
        source?: string;
        type?: string;
        tags?: string[];
        page?: number;
        pageSize?: number;
    }) => Promise<void>;
    currentPage: number;
    setCurrentPage: (page: number) => void;
    query: string;
    setQuery: (query: string) => void;
    pageSize: number;
    isLoading: boolean;
    setPageSize: (size: number) => void;
    filters: {
        sources: Set<string>;
        tags: Set<string>;
        types: Set<string>;
    }
}

const AssetViewerContext = createContext<AssetViewerContextType | undefined>(undefined);

export const useAssets = () => {
    const context = useContext(AssetViewerContext);
    if (!context) {
        throw new Error('useAssets must be used within an AssetViewerProvider');
    }
    return context;
};

interface AssetViewerProviderProps {
    children: ReactNode;
}


export const AssetViewerProvider: React.FC<AssetViewerProviderProps> = ({ children }) => {
    const [assets, setAssets] = useState<AssetView>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [query, setQuery] = useState<string>("")
    const [currentPage, setCurrentPage] = useState(1);
    const [filters, setFilters] = useState({
        sources: [],
        tags: [],
        types: []
    });
    async function fetchAssets() {
        setIsLoading(true);
        setError(null);
        try {
            const data = await getAssets({
                query,
                page: currentPage,
                sources: filters.sources,
                tags: filters.tags,
                types: filters.types
            });
            setAssets(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unknown error occurred');
        } finally {
            setIsLoading(false);
        }
    }

    useEffect(() => {
        fetchAssets();
    }, [currentPage]);

    useEffect(() => {
        setCurrentPage(1);
    }, [filters, query])

    useEffect(() => {
        fetchAssets()
    }, [filters])

    const value = {
        assets,
        isLoading,
        error,
        // query,
        setQuery,
        fetchAssets,
        currentPage,
        setCurrentPage,
        filters,
        setFilters
    };

    return (
        <AssetViewerContext.Provider value={value}>
            {children}
        </AssetViewerContext.Provider>
    );
};
