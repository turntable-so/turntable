import { type ReactNode, createContext, useContext, useState } from "react";
import { getProjectBasedLineage } from "../actions/actions";

type LineageContextType = {
  lineageData: LineageData;
  fetchFileBasedLineage: ({
    filePath,
    branchId,
  }: {
    filePath: string;
    branchId: string;
  }) => Promise<void>;
  setFilePathToLoading: ({ loading, filePath }: { loading: boolean; filePath: string }) => void;
};

type LineageData = {
  [filePath: string]: {
    data: any;
    isLoading: boolean;
    error: string | null;
    assetOnly: boolean;
    predecessorDepth: number;
    successorDepth: number;
    lineageType: "all" | "direct_only";
  };
};

export const LineageContext = createContext<LineageContextType | undefined>(
  undefined,
);

export const LineageProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [lineageData, setLineageData] = useState<LineageData>({});

  const fetchFileBasedLineage = async ({
    filePath,
    branchId,
  }: {
    filePath: string;
    branchId: string;
  }) => {
    if (!branchId || !filePath || !filePath.endsWith(".sql")) {
      return;
    }
    console.log("fetching lineage for", filePath);
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
      lineage_type: "all",
      successor_depth: 1,
      predecessor_depth: 1,
      asset_only: true,
    });
    if (result.error) {
      setLineageData((prev) => ({
        ...prev,
        [filePath]: {
          data: null,
          isLoading: false,
          error: result.error,
          assetOnly: true,
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
          assetOnly: true,
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
