import { type ReactNode, createContext, useContext, useState } from "react";
import { getProjectBasedLineage } from "../actions/actions";

type LineageContextType = {
  lineageData: {
    [filePath: string]: {
      data: any;
      isLoading: boolean;
      error: string | null;
    };
  };
  fetchFileBasedLineage: ({
    filePath,
    branchId,
    lineageType,
  }: {
    filePath: string;
    branchId: string;
    lineageType: "all" | "direct_only";
  }) => Promise<void>;
  setFilePathToLoading: ({ loading: boolean, filePath: string }) => void;
  assetOnly: boolean;
  setAssetOnly: (assetOnly: boolean) => void;
};

export const LineageContext = createContext<LineageContextType | undefined>(
  undefined,
);

export const LineageProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [lineageData, setLineageData] = useState({});
  const [assetOnly, setAssetOnly] = useState(true);
  const [loadingColumnLineage, setLoadingColumnLineage] = useState(false);

  const fetchFileBasedLineage = async ({
    filePath,
    branchId,
    lineageType,
  }: {
    filePath: string;
    branchId: string;
    lineageType: "all" | "direct_only";
  }) => {
    setLineageData((prev) => ({
      ...prev,
      [filePath]: {
        ...prev[filePath],
        isLoading: true,
        error: null,
      },
    }));
    const result = await getProjectBasedLineage({
      filePath,
      branchId,
      lineage_type: lineageType,
      successor_depth: 1,
      predecessor_depth: 1,
      asset_only: assetOnly,
    });
    if (result.error) {
      setLineageData((prev) => ({
        ...prev,
        [filePath]: {
          data: null,
          isLoading: false,
          error: result.error,
        },
      }));
    } else {
      const { lineage, root_asset } = result;
      setLineageData((prev) => ({
        ...prev,
        [filePath]: {
          data: { lineage, root_asset },
          isLoading: false,
          error: null,
        },
      }));
    }
  };

  const setFilePathToLoading = ({
    loading,
    filePath,
  }: { loading: boolean; filePath: string }) => {
    setLineageData((prev) => ({
      ...prev,
      [filePath]: {
        ...prev[filePath],
        isLoading: loading,
      },
    }));
  };

  return (
    <LineageContext.Provider
      value={{
        lineageData,
        fetchFileBasedLineage,
        setFilePathToLoading,
        assetOnly,
        setAssetOnly,
      }}
    >
      {children}
    </LineageContext.Provider>
  );
};

export const useLineage = () => {
  const context = useContext(LineageContext);
  if (context === undefined) {
    throw new Error("useLineage must be used within a LineageProvider");
  }
  return context;
};
