export const TURNTABLE_LOCAL_STORAGE_PREFIX = "turntable-";
const TRUNCATE_LIMIT = 8;

const truncateBranchId = (branchId: string): string => {
  return branchId.substring(0, TRUNCATE_LIMIT);
};

const createLocalStorageKey = (branchId: string, suffix: string): string => {
  return `${TURNTABLE_LOCAL_STORAGE_PREFIX}${truncateBranchId(branchId)}-${suffix}`;
};

export const LocalStorageKeys = {
  bottomPanelTab: (branchId: string): string =>
    createLocalStorageKey(branchId, "bottom-panel-tab"),
  commandHistory: (branchId: string): string =>
    createLocalStorageKey(branchId, "command-history"),
  recentCommands: (branchId: string): string =>
    createLocalStorageKey(branchId, "recent-commands"),
  recentFiles: (branchId: string): string =>
    createLocalStorageKey(branchId, "recent-files"),
  fileTabs: (branchId: string): string =>
    createLocalStorageKey(branchId, "file-tabs"),
  activeFile: (branchId: string): string =>
    createLocalStorageKey(branchId, "active-file-tab-index"),
  checkForProblemsOnEdit: (branchId: string): string =>
    createLocalStorageKey(branchId, "check-for-problems-on-edit"),
  formatOnSave: (branchId: string): string =>
    createLocalStorageKey(branchId, "format-on-save"),
  aiMessageHistory: (branchId: string): string =>
    createLocalStorageKey(branchId, "ai-message-history"),
};
