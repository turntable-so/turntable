import { LocalStorageKeys } from "@/app/constants/local-storage-keys";
import {
  type Dispatch,
  type ReactNode,
  type SetStateAction,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { toast } from "sonner";
import { useDebounceValue, useLocalStorage } from "usehooks-ts";
import {
  changeFilePath,
  cloneBranchAndMount,
  commit,
  compileDbtQuery,
  createFile,
  deleteFile,
  discardBranchChanges,
  duplicateFileOrFolder,
  executeQueryPreview,
  fetchFileContents,
  formatDbtQuery,
  getFileIndex,
  getProject,
  getProjectChanges,
  moveFileOrDirectory,
  persistFile,
} from "../actions/actions";
import {
  getDownloadableFile,
  validateDbtQuery,
} from "../actions/client-actions";
import type { Lineage } from "./LineageView";

export const MAX_RECENT_COMMANDS = 5;

type NodeType = "file" | "directory" | "url" | "loader" | "error";

type FileView = "edit" | "diff" | "new" | "apply";

export type FileNode = {
  name: string;
  path: string;
  type: NodeType;
  children?: FileNode[];
};

export type OpenedFile = {
  node: FileNode;
  content: string | ReactNode;
  isDirty: boolean;
  view: FileView;
  diff?: {
    original: string;
    modified: string;
  };
};

export type ProblemState = {
  loading: boolean;
  data: Array<{ message: string }>;
};

type FilesContextType = {
  files: FileNode[];
  openedFiles: OpenedFile[];
  openFile: (node: FileNode) => void;
  openUrl: ({
    id,
    name,
    url,
  }: {
    id: string;
    name: string;
    url: string;
  }) => void;
  openLoader: ({ id, name }: { id: string; name: string }) => void;
  closeFile: (file: OpenedFile) => void;
  activeFile: OpenedFile | null;
  setActiveFile: React.Dispatch<React.SetStateAction<OpenedFile | null>>;
  updateFileContent: (path: string, content: string) => void;
  updateLoaderContent: ({
    path,
    content,
    newNodeType,
  }: {
    path: string;
    content: string | ReactNode;
    newNodeType: NodeType;
  }) => void;
  saveFile: (path: string, content: string) => void;
  searchFileIndex: FileNode[];
  openError: (params: {
    id: string;
    name: string;
    errorMessage: string;
    buttonLabel: string;
    buttonOnClick: () => void;
  }) => void;
  createFileAndRefresh: (
    path: string,
    fileContents: string,
    isDirectory: boolean,
  ) => void;
  deleteFileAndRefresh: (path: string) => void;
  duplicateFileOrFolderAndRefresh: (filePath: string) => void;
  createNewFileTab: () => void;
  changes: Changes | null;
  fetchChanges: (branchId: string) => void;
  recentFiles: FileNode[]; // New state added here
  fetchFiles: () => void;
  branchId: string;
  branchName: string;
  sourceBranch: string;
  readOnly: boolean | undefined;
  isCloned: boolean | undefined;
  schema: string | undefined;
  fetchBranch: (branchId: string) => Promise<void>;
  cloneBranch: (branchId: string) => Promise<void>;
  commitChanges: (
    commitMessage: string,
    filePaths: string[],
  ) => Promise<boolean>;
  pullRequestUrl: string | undefined;
  isCloning: boolean;
  discardChanges: (branchId: string) => Promise<void>;
  debouncedActiveFileContent: string;
  problems: ProblemState;
  checkForProblemsOnEdit: boolean;
  setCheckForProblemsOnEdit: Dispatch<SetStateAction<boolean>>;
  renameFile: (filePath: string, newPath: string) => Promise<boolean>;
  formatActiveFile: () => Promise<void>;
  formatOnSave: boolean;
  setFormatOnSave: Dispatch<SetStateAction<boolean>>;
  createDirectoryAndRefresh: (path: string) => Promise<void>;
  filesLoading: boolean;
  downloadFile: (path: string) => Promise<void>;
  compileActiveFile: (filename: string) => Promise<void>;
  compiledSql: { sql: string; file_name: string } | null;
  isCompiling: boolean;
  compileError: string | null;
  showConfirmSaveDialog: boolean;
  setShowConfirmSaveDialog: Dispatch<SetStateAction<boolean>>;
  fileToClose: OpenedFile | null;
  setFileToClose: Dispatch<SetStateAction<OpenedFile | null>>;
  closeFilesToLeft: (file: OpenedFile) => void;
  closeFilesToRight: (file: OpenedFile) => void;
  closeAllOtherFiles: (file: OpenedFile) => void;
  closeAllFiles: () => void;
  runQueryPreview: (content?: string) => Promise<void>;
  queryPreview: QueryPreview | null;
  queryPreviewError: string | null;
  isQueryPreviewLoading: boolean;
  setIsQueryPreviewLoading: Dispatch<SetStateAction<boolean>>;
  lineageData: Record<
    string,
    {
      isLoading: boolean;
      data: Lineage | null;
      error: string | null;
      showColumns: boolean;
    }
  >;
  setLineageData: Dispatch<
    SetStateAction<
      Record<
        string,
        {
          isLoading: boolean;
          data: Lineage | null;
          error: string | null;
          showColumns: boolean;
        }
      >
    >
  >;
  isSqlFile: boolean;
  queryPreviewData: {
    rows: any[];
    cols: any[];
    file_name: string;
  } | null;
  setQueryPreviewData: Dispatch<
    SetStateAction<{
      rows: any[];
      cols: any[];
      file_name: string;
    } | null>
  >;
  isApplying: boolean;
  setIsApplying: Dispatch<SetStateAction<boolean>>;
  move: (dragIds: string[], parentId: string) => Promise<boolean>;
};

type QueryPreview = {
  rows?: Object;
  signed_url: string;
};

const FilesContext = createContext<FilesContextType | undefined>(undefined);

const defaultFileTab = {
  node: {
    name: "new_tab",
    path: `Untitled-${crypto.randomUUID()}`,
    type: "file",
  },
  content: "",
  isDirty: false,
  view: "new",
};

type Changes = Array<{
  path: string;
  before: string;
  after: string;
  type: "untracked" | "modified" | "deleted";
}>;

export const FilesProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [branchId, setBranchId] = useState("");
  const [branchName, setBranchName] = useState("");
  const [sourceBranch, setSourceBranch] = useState("");
  const [filesLoading, setFilesLoading] = useState(false);
  const [readOnly, setReadOnly] = useState<boolean | undefined>(undefined);
  const [isCloned, setIsCloned] = useState<boolean | undefined>(undefined);
  const [queryPreview, setQueryPreview] = useState<QueryPreview | null>(null);
  const [isQueryPreviewLoading, setIsQueryPreviewLoading] = useState(false);
  const [queryPreviewError, setQueryPreviewError] = useState<string | null>(
    null,
  );
  const [pullRequestUrl, setPullRequestUrl] = useState<string | undefined>(
    undefined,
  );
  const [files, setFiles] = useState<FileNode[]>([]);
  const [schema, setSchema] = useState<string | undefined>(undefined);
  const [openedFiles, setOpenedFiles] = useLocalStorage<OpenedFile[]>(
    LocalStorageKeys.fileTabs(branchId),
    [defaultFileTab as OpenedFile],
  );
  const [activeFile, setActiveFile] = useLocalStorage<OpenedFile | null>(
    LocalStorageKeys.activeFile(branchId),
    openedFiles[0] || null,
  );
  const [debouncedActiveFileContent] = useDebounceValue<string>(
    String(activeFile?.content || ""),
    350,
  );
  const [problems, setProblems] = useState<ProblemState>({
    loading: false,
    data: [],
  });
  const [searchFileIndex, setSearchFileIndex] = useState<FileNode[]>([]);
  const [changes, setChanges] = useState<Changes | null>(null);
  const [recentFiles, setRecentFiles] = useLocalStorage<FileNode[]>(
    LocalStorageKeys.recentFiles(branchId),
    [],
  );
  const [isCompiling, setIsCompiling] = useState(false);
  const [compiledSql, setCompiledSql] = useState<{
    sql: string;
    file_name: string;
  } | null>(null);
  const [compileError, setCompileError] = useState<string | null>(null);
  const [isCloning, setIsCloning] = useState(false);
  const [checkForProblemsOnEdit, setCheckForProblemsOnEdit] = useLocalStorage(
    LocalStorageKeys.checkForProblemsOnEdit(branchId),
    false,
  );
  const [formatOnSave, setFormatOnSave] = useLocalStorage(
    LocalStorageKeys.formatOnSave(branchId),
    false,
  );
  const formatOnSaveRef = useRef(formatOnSave);
  useEffect(() => {
    formatOnSaveRef.current = formatOnSave;
  }, [formatOnSave]);
  const [showConfirmSaveDialog, setShowConfirmSaveDialog] = useState(false);
  const [fileToClose, setFileToClose] = useState<OpenedFile | null>(null);
  const [lineageData, setLineageData] = useState<
    Record<
      string,
      {
        isLoading: boolean;
        data: Lineage | null;
        error: string | null;
        showColumns: boolean;
      }
    >
  >({});
  const isSqlFile = activeFile?.node.name.endsWith(".sql") ?? false;
  const [queryPreviewData, setQueryPreviewData] = useState<{
    rows: any[];
    cols: any[];
    file_name: string;
  } | null>(null);
  const [isApplying, setIsApplying] = useState(false);

  const fetchBranch = async (id: string) => {
    if (id) {
      const project = await getProject(id);
      setBranchId(project.id);
      setBranchName(project.name);
      setReadOnly(project.read_only);
      setIsCloned(project.is_cloned);
      setPullRequestUrl(project.pull_request_url);
      setSchema(project.schema);
      setSourceBranch(project.source_branch);
    }
  };

  const discardChanges = async (branchId: string) => {
    await discardBranchChanges(branchId);
    fetchChanges(branchId);
    fetchFiles();
  };

  const cloneBranch = async (branchId: string) => {
    setIsCloning(true);
    const branch = await cloneBranchAndMount(branchId);
    setIsCloning(false);
    setIsCloned(true);
  };

  const fetchChanges = async (branchId: string) => {
    const result = await getProjectChanges(branchId);
    const flattenedChanges = result.untracked
      .map((change) => ({
        ...change,
        type: "untracked",
      }))
      .concat(
        result.modified.map((change) => ({
          ...change,
          type: "modified",
        })),
      )
      .concat(
        result.deleted.map((change) => ({
          ...change,
          type: "deleted",
        })),
      );
    setChanges(flattenedChanges as Changes);
  };

  const fetchFiles = async () => {
    setFilesLoading(true);
    const { file_index } = await getFileIndex(branchId);
    const fileIndex = file_index.map((file: FileNode) => ({ ...file }));
    const sortFileTree = (files: FileNode[]): FileNode[] => {
      return files
        .sort((a, b) => a.name.localeCompare(b.name))
        .map((file) => {
          if (file.type === "directory" && file.children) {
            return {
              ...file,
              children: sortFileTree(file.children),
            };
          }
          return file;
        });
    };
    const sortedFileIndex = sortFileTree(fileIndex);
    setFiles(sortedFileIndex);
    const flattenFileIndex = (files: FileNode[]): FileNode[] => {
      return files.reduce((acc: FileNode[], file: FileNode) => {
        if (file.type === "directory" && file.children) {
          return [...acc, file, ...flattenFileIndex(file.children)];
        }
        return [...acc, file];
      }, []);
    };

    const flattenedFiles = flattenFileIndex(fileIndex);
    const searchableFiles = flattenedFiles.filter(
      (file) =>
        file.type === "file" &&
        !file.path.includes("dbt_packages/") &&
        !file.path.includes("target/"),
    );
    setSearchFileIndex(searchableFiles);

    // Filter out files that no longer exist
    const filePaths = new Set(flattenedFiles.map(file => file.path));
    setRecentFiles(prevRecentFiles =>
      prevRecentFiles.filter(file => filePaths.has(file.path))
    );
    setOpenedFiles(prevOpenedFiles =>
      prevOpenedFiles.filter(file =>
        file.node.type === "file" ? filePaths.has(file.node.path) : true
      )
    );

    setFilesLoading(false);
  };

  const openError = useCallback(
    ({
      id,
      name,
      errorMessage,
    }: {
      id: string;
      name: string;
      errorMessage: string;
    }) => {
      const errorNode: FileNode = {
        name,
        path: id,
        type: "error",
      };

      const openedFileNode: OpenedFile = {
        node: errorNode,
        content: errorMessage,
        isDirty: false,
        view: "edit",
      };

      setOpenedFiles((prev) => [...prev, openedFileNode]);
      setActiveFile(openedFileNode);
    },
    [setOpenedFiles, setActiveFile],
  );

  const openFile = useCallback(
    async (node: FileNode) => {
      if (node.type !== "file") {
        return;
      }

      const existingFile = openedFiles.find((f) => f.node.path === node.path);
      if (!existingFile) {
        const { contents, error } = await fetchFileContents({
          branchId,
          path: node.path,
        });
        if (error === "FILE_NOT_FOUND") {
          alert("We couldn't find this file. Please try again.");
          return;
        }
        if (error === "FILE_EXCEEDS_SIZE_LIMIT") {
          openError({
            id: node.path,
            name: node.name,
            errorMessage: "FILE_EXCEEDS_SIZE_LIMIT",
          });
          return;
        }
        if (error) {
          alert("Something went wrong. Please try again.");
          return;
        }
        const newFile: OpenedFile = {
          node,
          content: contents,
          isDirty: false,
          view: "edit",
        };
        setOpenedFiles((prev) => {
          return [...prev, newFile];
        });
        setActiveFile(newFile);
      } else {
        setActiveFile(existingFile);
      }

      setRecentFiles((prevRecentFiles) => {
        const updatedRecentFiles = prevRecentFiles.filter(
          (file) => file.path !== node.path,
        );
        updatedRecentFiles.unshift(node);
        if (updatedRecentFiles.length > MAX_RECENT_COMMANDS) {
          updatedRecentFiles.pop();
        }
        return updatedRecentFiles;
      });
    },
    [openedFiles, branchId],
  );

  const openUrl = useCallback(
    ({ id, name, url }: { id: string; name: string; url: string }) => {
      const urlNode: FileNode = {
        name,
        path: id,
        type: "url",
      };

      const newUrl: OpenedFile = {
        node: urlNode,
        content: url,
        isDirty: false,
        view: "edit",
      };

      setOpenedFiles((prev) => [...prev, newUrl]);
      setActiveFile(newUrl);
    },
    [openedFiles],
  );

  const openLoader = useCallback(
    ({ id, name }: { id: string; name: string }) => {
      const loaderNode: FileNode = {
        name,
        path: id,
        type: "loader",
      };

      const openedFileNode: OpenedFile = {
        node: loaderNode,
        content: "",
        isDirty: false,
        view: "edit",
      };

      setOpenedFiles((prev) => [...prev, openedFileNode]);
      setActiveFile(openedFileNode);
    },
    [openedFiles],
  );

  const closeFile = useCallback(
    (file: OpenedFile) => {
      if (file.isDirty) {
        setFileToClose(file);
        setShowConfirmSaveDialog(true);
        return;
      }

      const newOpenedFiles = openedFiles.filter(
        (f) => f.node.path !== file.node.path,
      );
      setOpenedFiles(newOpenedFiles);
      if (newOpenedFiles.length === 0) {
        setOpenedFiles([defaultFileTab as OpenedFile]);
        setActiveFile(defaultFileTab as OpenedFile);
      } else if (file.node.path === activeFile?.node.path) {
        if (newOpenedFiles.length > 0) {
          setActiveFile(newOpenedFiles[0]);
        } else {
          setActiveFile(null);
        }
      }
    },
    [openedFiles, activeFile],
  );

  const downloadFile = async (path: string) => {
    const response = await getDownloadableFile({
      branchId,
      path,
    });

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = path.split("/").pop() || "download";
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const createFileAndRefresh = async (
    path: string,
    fileContents: string,
    isDirectory: boolean,
  ) => {
    await createFile(branchId, path, isDirectory, fileContents);
    await fetchFiles();
  };

  const duplicateFileOrFolderAndRefresh = async (filePath: string) => {
    const success = await duplicateFileOrFolder({
      branchId,
      filePath,
    });
    if (!success) {
      toast.error("Failed to duplicate file");
    }
    await fetchFiles();
  };

  const updateLoaderContent = useCallback(
    ({
      path,
      content,
      newNodeType,
    }: {
      path: string;
      content: string | ReactNode;
      newNodeType: NodeType;
    }) => {
      setOpenedFiles((prev) =>
        prev.map((f) =>
          f.node.path === path
            ? {
              ...f,
              content,
              node: { ...f.node, type: newNodeType },
            }
            : f,
        ),
      );
      setActiveFile((prev) => {
        if (prev?.node?.path === path) {
          return {
            ...prev,
            node: { ...prev.node, type: newNodeType },
            content,
          };
        }
        return prev;
      });
    },
    [],
  );

  const updateFileContent = useCallback((path: string, content: string) => {
    setOpenedFiles((prev) =>
      prev.map((f) =>
        f.node.path === path ? { ...f, content, isDirty: true } : f,
      ),
    );
    setActiveFile((prev) =>
      prev?.node.path === path ? { ...prev, content, isDirty: true } : prev,
    );
  }, []);

  const saveFile = async (filepath: string, content: string) => {
    if (!activeFile) {
      return;
    }

    const result = await persistFile({
      branchId,
      filePath: filepath,
      fileContents: content,
      format: formatOnSaveRef.current,
    });
    const newContent = result.content;
    setOpenedFiles((prev) =>
      prev.map((f) =>
        f.node.path === filepath
          ? { ...f, isDirty: false, content: newContent }
          : f,
      ),
    );
    setActiveFile((prev) =>
      prev?.node.path === filepath ? { ...prev, content: newContent } : prev,
    );
  };

  const deleteFileAndRefresh = async (filepath: string) => {
    await deleteFile(branchId, filepath);
    await fetchFiles();
  };

  const createNewFileTab = () => {
    const newTab: OpenedFile = {
      node: {
        name: "new_tab",
        path: `Untitled-${crypto.randomUUID()}`,
        type: "file",
      },
      content: "",
      isDirty: false,
      view: "new",
    };
    setOpenedFiles((prev) => [...prev, newTab]);
    setActiveFile(newTab);
  };

  const commitChanges = async (commitMessage: string, filePaths: string[]) => {
    const result = await commit(branchId, commitMessage, filePaths);
    fetchChanges(branchId);
    return result;
  };

  const validateQuery = async (query: string, signal?: AbortSignal) => {
    try {
      setProblems((prev) => ({ ...prev, loading: true, data: [] }));
      const data = await validateDbtQuery(
        {
          query,
          project_id: branchId,
        },
        signal,
      );

      if (data.error) {
        setProblems((prev) => ({
          ...prev,
          loading: false,
          data: [{ message: data.error }],
        }));
        return;
      }

      if (!data.errors) {
        setProblems((prev) => ({
          ...prev,
          loading: false,
          data: [],
        }));
        return;
      }

      const formattedProblems = data.errors.map((error: any) => ({
        message: error.msg,
      }));
      setProblems((prev) => ({
        ...prev,
        loading: false,
        data: formattedProblems,
      }));
    } catch (e: any) {
      if (e instanceof Error && e.name === "AbortError") {
        return;
      }
      setProblems((prev) => ({
        ...prev,
        loading: false,
        data: [{ message: "An error occurred while validating the query" }],
      }));
    }
  };

  useEffect(() => {
    if (!isSqlFile) {
      setProblems((prev) => ({ ...prev, data: [] }));
      return;
    }

    if (
      debouncedActiveFileContent &&
      typeof debouncedActiveFileContent === "string" &&
      checkForProblemsOnEdit
    ) {
      const abortController = new AbortController();
      const signal = abortController.signal;

      validateQuery(debouncedActiveFileContent, signal);

      return () => {
        abortController.abort();
      };
    }
  }, [debouncedActiveFileContent, checkForProblemsOnEdit, isSqlFile]);

  useEffect(() => {
    if (!checkForProblemsOnEdit) {
      setProblems((prev) => ({ ...prev, data: [] }));
    }
  }, [checkForProblemsOnEdit]);

  const renameFile = async (filePath: string, newPath: string) => {
    const success = await changeFilePath(branchId, filePath, newPath);
    fetchFiles();
    return success;
  };

  const move = async (dragIds: string[], parentId: string) => {
    await moveFileOrDirectory(branchId, dragIds, parentId);
    fetchFiles();
    return true
  };

  const formatActiveFile = async () => {
    if (
      !activeFile ||
      !activeFile.content ||
      typeof activeFile.content !== "string"
    ) {
      return;
    }
    const formattedQuery = await formatDbtQuery({
      query: activeFile.content,
    });
    updateFileContent(activeFile.node.path, formattedQuery);
  };

  const createDirectoryAndRefresh = async (path: string) => {
    await createFile(branchId, path, true, "");
    await fetchFiles();
  };

  const compileActiveFile = async (filename: string) => {
    setIsCompiling(true);
    setCompileError(null);
    setCompiledSql(null);
    const result = await compileDbtQuery(branchId, {
      filepath: activeFile?.node.path || "",
    });
    if (result.error) {
      setCompileError(result.error);
    } else {
      setCompiledSql({
        sql: result,
        file_name: filename,
      });
    }
    setIsCompiling(false);
  };

  const closeFilesToLeft = useCallback(
    (file: OpenedFile) => {
      const fileIndex = openedFiles.findIndex(
        (f) => f.node.path === file.node.path,
      );
      if (fileIndex > 0) {
        const filesToClose = openedFiles.slice(0, fileIndex);
        const dirtyFilesToKeep = filesToClose.filter((f) => f.isDirty);
        const newOpenedFiles = [
          ...dirtyFilesToKeep,
          ...openedFiles.slice(fileIndex),
        ];
        setOpenedFiles(newOpenedFiles);
        if (!newOpenedFiles.includes(activeFile)) {
          setActiveFile(newOpenedFiles[0] || null);
        }
      }
    },
    [openedFiles, activeFile],
  );

  const closeFilesToRight = useCallback(
    (file: OpenedFile) => {
      const fileIndex = openedFiles.findIndex(
        (f) => f.node.path === file.node.path,
      );
      if (fileIndex >= 0 && fileIndex < openedFiles.length - 1) {
        const filesToClose = openedFiles.slice(fileIndex + 1);
        const dirtyFilesToKeep = filesToClose.filter((f) => f.isDirty);
        const newOpenedFiles = [
          ...openedFiles.slice(0, fileIndex + 1),
          ...dirtyFilesToKeep,
        ];
        setOpenedFiles(newOpenedFiles);
        if (!newOpenedFiles.includes(activeFile)) {
          setActiveFile(newOpenedFiles[newOpenedFiles.length - 1] || null);
        }
      }
    },
    [openedFiles, activeFile],
  );

  const closeAllOtherFiles = useCallback(
    (file: OpenedFile) => {
      const filesToKeep = openedFiles.filter(
        (f) => f.isDirty || f.node.path === file.node.path,
      );
      setOpenedFiles(filesToKeep);
      setActiveFile(file);
    },
    [openedFiles],
  );

  const closeAllFiles = useCallback(() => {
    const dirtyFilesToKeep = openedFiles.filter((f) => f.isDirty);
    setOpenedFiles(dirtyFilesToKeep);
    if (!dirtyFilesToKeep.includes(activeFile)) {
      setActiveFile(dirtyFilesToKeep[0] || null);
    }
  }, [openedFiles, activeFile]);

  const runQueryPreview = useCallback(
    async (content?: string) => {
      setIsQueryPreviewLoading(true);
      setQueryPreview(null);
      setQueryPreviewError(null);
      if (
        content ||
        (activeFile?.content && typeof activeFile.content === "string")
      ) {
        const dbtSql = content || activeFile?.content;
        const preview = await executeQueryPreview({ dbtSql, branchId });
        if (preview.error) {
          setQueryPreviewError(preview.error);
        } else {
          setQueryPreview(preview);
        }
      }
      setIsQueryPreviewLoading(false);
    },
    [activeFile],
  );

  return (
    <FilesContext.Provider
      value={{
        files,
        openedFiles,
        openFile,
        openUrl,
        openLoader,
        closeFile,
        activeFile,
        setActiveFile,
        updateFileContent,
        updateLoaderContent,
        saveFile,
        searchFileIndex,
        createFileAndRefresh,
        deleteFileAndRefresh,
        duplicateFileOrFolderAndRefresh,
        createNewFileTab,
        changes,
        fetchChanges,
        fetchFiles,
        recentFiles,
        branchId,
        branchName,
        sourceBranch,
        readOnly,
        isCloned,
        fetchBranch,
        cloneBranch,
        commitChanges,
        pullRequestUrl,
        isCloning,
        discardChanges,
        schema,
        debouncedActiveFileContent,
        problems,
        checkForProblemsOnEdit,
        setCheckForProblemsOnEdit,
        renameFile,
        formatActiveFile,
        formatOnSave,
        setFormatOnSave,
        createDirectoryAndRefresh,
        filesLoading,
        downloadFile,
        openError,
        compileActiveFile,
        isCompiling,
        compiledSql,
        compileError,
        showConfirmSaveDialog,
        setShowConfirmSaveDialog,
        fileToClose,
        setFileToClose,
        closeFilesToLeft,
        closeFilesToRight,
        closeAllOtherFiles,
        closeAllFiles,
        runQueryPreview,
        queryPreview,
        queryPreviewError,
        isQueryPreviewLoading,
        setIsQueryPreviewLoading,
        lineageData,
        setLineageData,
        isSqlFile,
        queryPreviewData,
        setQueryPreviewData,
        isApplying,
        setIsApplying,
        move,
      }}
    >
      {children}
    </FilesContext.Provider>
  );
};

export const useFiles = () => {
  const context = useContext(FilesContext);
  if (context === undefined) {
    throw new Error("useFiles must be used within a FilesProvider");
  }
  return context;
};
