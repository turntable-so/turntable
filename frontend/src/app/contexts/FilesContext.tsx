import { LocalStorageKeys } from "@/app/constants/local-storage-keys";
import {
  type ReactNode,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { useLocalStorage } from "usehooks-ts";
import {
  type ProjectChanges,
  cloneBranchAndMount,
  commit,
  createFile,
  deleteFile,
  fetchFileContents,
  getBranch,
  getFileIndex,
  getProjectChanges,
  persistFile,
} from "../actions/actions";
import { useEditor } from "./EditorContext";

export const MAX_RECENT_COMMANDS = 5;

type NodeType = "file" | "directory" | "url" | "loader" | "error";

type FileView = "edit" | "diff" | "new";

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
  setActiveFile: (file: OpenedFile | null) => void;
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
  createFileAndRefresh: (path: string, fileContents: string) => void;
  deleteFileAndRefresh: (path: string) => void;
  createNewFileTab: () => void;
  changes: ProjectChanges | null;
  fetchChanges: () => void;
  recentFiles: FileNode[]; // New state added here
  fetchFiles: () => void;
  branchId: string;
  branchName: string;
  readOnly: boolean | undefined;
  isCloned: boolean | undefined;
  fetchBranch: (branchId: string) => Promise<void>;
  cloneBranch: (branchId: string) => Promise<void>;
  commitChanges: (commitMessage: string, filePaths: string[]) => Promise<void>;
};

const FilesContext = createContext<FilesContextType | undefined>(undefined);

type Changes = Array<{
  path: string;
  before: string;
  after: string;
  type: "untracked" | "modified" | "staged";
}>;

export const FilesProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [branchId, setBranchId] = useState("");
  const [branchName, setBranchName] = useState("");
  const [readOnly, setReadOnly] = useState<boolean | undefined>(undefined);
  const [isCloned, setIsCloned] = useState<boolean | undefined>(undefined);
  const [files, setFiles] = useState<FileNode[]>([]);
  const [openedFiles, setOpenedFiles] = useState<OpenedFile[]>([
    {
      node: {
        name: "New tab",
        path: `Untitled-${crypto.randomUUID()}`,
        type: "file",
      },
      content: "",
      isDirty: false,
      view: "new",
    },
  ]);
  const [activeFile, setActiveFile] = useState<OpenedFile | null>(
    openedFiles[0] || null,
  );
  const [searchFileIndex, setSearchFileIndex] = useState<FileNode[]>([]);
  const [changes, setChanges] = useState<Changes | null>(null);
  const [recentFiles, setRecentFiles] = useLocalStorage<FileNode[]>(
    LocalStorageKeys.recentFiles,
    [],
  );

  const fetchBranch = async (branchId: string) => {
    const branch = await getBranch(branchId);
    setBranchId(branch.id);
    setBranchName(branch.name);
    setReadOnly(branch.read_only);
    setIsCloned(branch.is_cloned);
  }

  const cloneBranch = async (branchId: string) => {
    const branch = await cloneBranchAndMount(branchId);
    setIsCloned(true);
  }

  const fetchChanges = async () => {
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
        result.staged.map((change) => ({
          ...change,
          type: "staged",
        })),
      );
    setChanges(flattenedChanges as Changes);
  };

  const fetchFiles = async () => {
    const { file_index } = await getFileIndex(branchId);
    const fileIndex = file_index.map((file: FileNode) => ({ ...file }));
    setFiles(fileIndex);
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
  };


  const openFile = useCallback(
    async (node: FileNode) => {
      if (node.type === "file") {
        const existingFile = openedFiles.find((f) => f.node.path === node.path);
        if (!existingFile) {
          const { contents } = await fetchFileContents(branchId, node.path);
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
      }
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
      const newOpenedFiles = openedFiles.filter(
        (f) => f.node.path !== file.node.path,
      );
      setOpenedFiles(newOpenedFiles);
      if (newOpenedFiles.length > 0) {
        setActiveFile(newOpenedFiles[0]);
      }
    },
    [openedFiles],
  );

  const createFileAndRefresh = async (path: string, fileContents: string) => {
    await createFile(branchId, path, fileContents);
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
  }, []);

  const saveFile = async (filepath: string, content: string) => {
    if (activeFile) {
      await persistFile(branchId, filepath, content);
      setOpenedFiles((prev) =>
        prev.map((f) =>
          f.node.path === filepath ? { ...f, isDirty: false, content } : f,
        ),
      );
    }
  };

  const deleteFileAndRefresh = async (filepath: string) => {
    await deleteFile(branchId, filepath);
    await fetchFiles();
  };

  const createNewFileTab = () => {
    const newTab: OpenedFile = {
      node: {
        name: "New tab",
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

    await commit(branchId, commitMessage, filePaths);
    fetchChanges();
  }

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
        createNewFileTab,
        changes,
        fetchChanges,
        fetchFiles,
        recentFiles,
        branchId,
        branchName,
        readOnly,
        isCloned,
        fetchBranch,
        cloneBranch,
        commitChanges
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
