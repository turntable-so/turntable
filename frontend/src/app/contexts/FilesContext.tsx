import React, { createContext, useContext, useState, useCallback, ReactNode, useEffect } from 'react';
import { createFile, deleteFile, fetchFileContents, getFileIndex, persistFile } from '../actions/actions';

export type FileNode = {
    name: string;
    path: string;
    type: 'file' | 'directory';
    children?: FileNode[];
};

export type OpenedFile = {
    node: FileNode;
    content: string;
    isDirty: boolean;
    view: 'edit' | 'diff' | 'new' | 'query';
    diff?: {
        original: string;
        modified: string;
    };
};

type FilesContextType = {
    files: FileNode[];
    openedFiles: OpenedFile[];
    openFile: (node: FileNode) => void;
    closeFile: (file: OpenedFile) => void;
    activeFile: OpenedFile | null;
    setActiveFile: (file: OpenedFile | null) => void;
    updateFileContent: (path: string, content: string) => void;
    saveFile: (path: string, content: string) => void;
    setActiveFilepath: (path: string) => void;
    activeFilepath: string | null;
    searchFileIndex: FileNode[];
    createFileAndRefresh: (path: string, fileContents: string) => void;
    deleteFileAndRefresh: (path: string) => void;
    createNewFileTab: () => void;
    createNewQueryTab: () => void;
};

const FilesContext = createContext<FilesContextType | undefined>(undefined);

export const FilesProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [files, setFiles] = useState<FileNode[]>([]);
    const [openedFiles, setOpenedFiles] = useState<OpenedFile[]>([
        {
            node: {
                name: 'New tab',
                path: `Untitled-${crypto.randomUUID()}`,
                type: 'file'
            },
            content: '',
            isDirty: false,
            view: 'new'
        }
    ]);
    const [activeFile, setActiveFile] = useState<OpenedFile | null>(
        openedFiles[0] || null
    );
    const [activeFilepath, setActiveFilepath] = useState<string | null>(null);
    const [searchFileIndex, setSearchFileIndex] = useState<FileNode[]>([]);

    const fetchFiles = async () => {
        const { dirty_changes, file_index } = await getFileIndex()
        console.log({ file_index })
        const fileIndex = file_index.map((file: FileNode) => ({ ...file }))
        setFiles(fileIndex)
        const flattenFileIndex = (files: FileNode[]): FileNode[] => {
            return files.reduce((acc: FileNode[], file: FileNode) => {
                if (file.type === 'directory' && file.children) {
                    return [...acc, file, ...flattenFileIndex(file.children)];
                }
                return [...acc, file];
            }, []);
        };

        const flattenedFiles = flattenFileIndex(fileIndex);
        const searchableFiles = flattenedFiles
            .filter(file => file.type === 'file')
            .filter(file => !file.path.includes('dbt_packages/'))
            .filter(file => !file.path.includes('target/'))
        setSearchFileIndex(searchableFiles)
    }

    useEffect(() => {
        fetchFiles()
    }, [])

    const openFile = useCallback(async (node: FileNode) => {
        console.log('openFile', { node })
        if (node.type === 'file') {
            console.log({ openedFiles })
            const existingFile = openedFiles.find(f => f.node.path === node.path);
            if (!existingFile) {
                const { contents } = await fetchFileContents(node.path)
                const newFile: OpenedFile = {
                    node,
                    content: contents,
                    isDirty: false,
                    view: 'edit'
                }
                setOpenedFiles(prev => [...prev, newFile]);
                setActiveFile(newFile);
                setActiveFilepath(node.path)
            } else {
                setActiveFile(existingFile);
                setActiveFilepath(node.path)
            }
        }
    }, [openedFiles]);

    const closeFile = useCallback((file: OpenedFile) => {
        const newOpenedFiles = openedFiles.filter(f => f.node.path !== file.node.path)
        setOpenedFiles(newOpenedFiles);
        console.log({ newOpenedFiles })
        if (newOpenedFiles.length > 0) {
            setActiveFile(newOpenedFiles[0]);
        }
    }, [openedFiles]);

    const createFileAndRefresh = async (path: string, fileContents: string) => {
        await createFile(path, fileContents);
        await fetchFiles()
    }


    const updateFileContent = useCallback((path: string, content: string) => {
        console.log({ openedFiles, path })
        setOpenedFiles(prev => prev.map(f =>
            f.node.path === path ? { ...f, content, isDirty: true } : f
        ));
    }, []);

    const saveFile = async (filepath: string, content: string) => {
        console.log('saveFile', { filepath });
        if (activeFile) {
            await persistFile(filepath, content);
            setOpenedFiles(prev => prev.map(f =>
                f.node.path === filepath ? { ...f, isDirty: false, content } : f
            ));
        }
    }

    const deleteFileAndRefresh = async (filepath: string) => {
        await deleteFile(filepath);
        await fetchFiles()
    }

    const createNewFileTab = () => {
        const newTab: OpenedFile = {
            node: {
                name: 'New tab',
                path: `Untitled-${crypto.randomUUID()}`,
                type: 'file'
            },
            content: '',
            isDirty: false,
            view: 'new'
        }
        setOpenedFiles(prev => [...prev, newTab]);
        setActiveFile(newTab);
    }

    const createNewQueryTab = () => {
        const newTab: OpenedFile = {
            node: {
                name: 'New query',
                path: `queries/${new Date().getTime()}.sql`,
                type: 'file'
            },
            content: '',
            isDirty: false,
            view: 'query'
        }
        setOpenedFiles(prev => [...prev, newTab]);
        setActiveFile(newTab);
    }


    return (
        <FilesContext.Provider value={{
            files,
            openedFiles,
            openFile,
            closeFile,
            activeFile,
            setActiveFile,
            updateFileContent,
            saveFile,
            setActiveFilepath,
            activeFilepath,
            searchFileIndex,
            createFileAndRefresh,
            deleteFileAndRefresh,
            createNewFileTab,
            createNewQueryTab
        }}>
            {children}
        </FilesContext.Provider>
    );
};

export const useFiles = () => {
    const context = useContext(FilesContext);
    if (context === undefined) {
        throw new Error('useFiles must be used within a FilesProvider');
    }
    return context;
};