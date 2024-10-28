import type React from "react";
import {
  type ReactNode,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import {
  createFile,
  deleteFile,
  fetchFileContents,
  getFileIndex,
  persistFile,
} from "../actions/actions";

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
  }: { id: string; name: string; url: string }) => void;
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
    content: string;
    newNodeType: NodeType;
  }) => void;
  saveFile: (path: string, content: string) => void;
  searchFileIndex: FileNode[];
  createFileAndRefresh: (path: string, fileContents: string) => void;
  deleteFileAndRefresh: (path: string) => void;
  createNewFileTab: () => void;
};

const FilesContext = createContext<FilesContextType | undefined>(undefined);

export const FilesProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
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

  const fetchFiles = async () => {
    const { dirty_changes, file_index } = await getFileIndex();
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
    const searchableFiles = flattenedFiles
      .filter((file) => file.type === "file")
      .filter((file) => !file.path.includes("dbt_packages/"))
      .filter((file) => !file.path.includes("target/"));
    setSearchFileIndex(searchableFiles);
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const openFile = useCallback(
    async (node: FileNode) => {
      if (node.type === "file") {
        const existingFile = openedFiles.find((f) => f.node.path === node.path);
        if (!existingFile) {
          const { contents } = await fetchFileContents(node.path);
          const newFile: OpenedFile = {
            node,
            content: contents,
            isDirty: false,
            view: "edit",
          };
          setOpenedFiles((prev) => [...prev, newFile]);
          setActiveFile(newFile);
        } else {
          setActiveFile(existingFile);
        }
      }
    },
    [openedFiles],
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
    await createFile(path, fileContents);
    await fetchFiles();
  };

  const updateLoaderContent = useCallback(
    ({
      path,
      content,
      newNodeType,
    }: {
      path: string;
      content: string;
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
      await persistFile(filepath, content);
      setOpenedFiles((prev) =>
        prev.map((f) =>
          f.node.path === filepath ? { ...f, isDirty: false, content } : f,
        ),
      );
    }
  };

  const deleteFileAndRefresh = async (filepath: string) => {
    await deleteFile(filepath);
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
