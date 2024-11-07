import {LocalStorageKeys} from "@/app/constants/local-storage-keys";
import {useLocalStorage} from "usehooks-ts";

type UseBottomPanelTabsProps = {
  branchId: string;
};

export const useBottomPanelTabs = ({ branchId }: UseBottomPanelTabsProps) => {
  return useLocalStorage<"lineage" | "results" | "command">(
    LocalStorageKeys.bottomPanelTab(branchId),
    "lineage",
  );
};
