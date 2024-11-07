function truncateBranchId(branchId: string): string {
  return branchId.substring(0, 8);
}

export const LocalStorageKeys = {
  bottomPanelTab: (branchId: string): string =>
    `${truncateBranchId(branchId)}-bottom-panel-tab`,
  commandHistory: (branchId: string): string =>
    `${truncateBranchId(branchId)}-command-history`,
  recentFiles: (branchId: string): string =>
    `${truncateBranchId(branchId)}-recent-files`,
  fileTabs: (branchId: string): string =>
    `${truncateBranchId(branchId)}-file-tabs`,
  activeFile: (branchId: string): string =>
    `${truncateBranchId(branchId)}-active-file-tab-index`,
};
