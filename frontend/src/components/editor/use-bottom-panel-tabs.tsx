import { LocalStorageKeys } from "@/app/constants/local-storage-keys";
import { useLocalStorage } from "usehooks-ts";

export const useBottomPanelTabs = () => {
  return useLocalStorage<"lineage" | "results" | "command">(
    LocalStorageKeys.bottomPanelTab,
    "lineage",
  );
};
