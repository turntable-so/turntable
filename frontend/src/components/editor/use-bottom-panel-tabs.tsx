import { useLocalStorage } from "usehooks-ts";
import { LocalStorageKeys } from "@/app/constants/local-storage-keys";

export const useBottomPanelTabs = () => {
  return useLocalStorage<"lineage" | "results" | "command">(
    LocalStorageKeys.bottomPanelTab,
    "lineage",
  );
};
