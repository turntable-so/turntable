import { getAssets, getColumns } from "@/app/actions/actions";
import type { SortingState } from "@tanstack/react-table";
import type React from "react";
import {
  type Dispatch,
  type ReactNode,
  type SetStateAction,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { current } from "tailwindcss/colors";

interface AssetViewerContextType {
  assets: any;
  error: string | null;
  submitSearch: () => void;
  currentPage: number;
  setCurrentPage: (page: number) => void;
  query: string;
  setQuery: (query: string) => void;
  isLoading: boolean;
  pageSize: number;
  filters: {
    sources: string[];
    tags: string[];
    types: string[];
  };
  setFilters: Dispatch<
    SetStateAction<{
      sources: string[];
      tags: string[];
      types: string[];
    }>
  >;
  sorting: SortingState;
  setSorting: Dispatch<SetStateAction<SortingState>>;
}

const AssetViewerContext = createContext<AssetViewerContextType | undefined>(
  undefined,
);

export const useAssets = () => {
  const context = useContext(AssetViewerContext);
  if (!context) {
    throw new Error("useAssets must be used within an AssetViewerProvider");
  }
  return context;
};

interface AssetViewerProviderProps {
  children: ReactNode;
}

export const AssetViewerProvider: React.FC<AssetViewerProviderProps> = ({
  children,
}) => {
  const pageSize = 50;
  const [assets, setAssets] = useState<any>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState<string>("");
  const [currentPage, setCurrentPage] = useState(1);
  const [sorting, setSorting] = useState<SortingState>([]);

  const [filters, setFilters] = useState<{
    sources: string[];
    tags: string[];
    types: string[];
  }>({
    sources: [],
    tags: [],
    types: [],
  });

  const fetchAssets = useCallback(
    async (page?: number) => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getAssets({
          query,
          page: page || currentPage,
          sources: filters.sources,
          tags: filters.tags,
          types: filters.types,
          sortBy: sorting[0]?.id,
          sortOrder: sorting[0]?.desc ? "desc" : "asc",
        });
        setAssets(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "An unknown error occurred",
        );
      } finally {
        setIsLoading(false);
      }
    },
    [query, currentPage, filters, sorting],
  );

  useEffect(() => {
    fetchAssets();
  }, [fetchAssets]);

  const submitSearch = useCallback(() => {
    setCurrentPage(1);
    fetchAssets(1);
  }, [fetchAssets]);

  const value: AssetViewerContextType = {
    assets,
    isLoading,
    error,
    query,
    setQuery,
    submitSearch,
    currentPage,
    setCurrentPage,
    filters,
    pageSize,
    setFilters,
    sorting,
    setSorting,
  };

  return (
    <AssetViewerContext.Provider value={value}>
      {children}
    </AssetViewerContext.Provider>
  );
};
