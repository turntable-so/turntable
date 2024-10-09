import React, { createContext, useContext, useState, useCallback, ReactNode, useEffect } from 'react';
import { fetchFileContents, getFileIndex, persistFile } from '../actions/actions';

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
    view: 'edit' | 'diff';
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
    saveActiveFile: () => void;
};

const FilesContext = createContext<FilesContextType | undefined>(undefined);

export const FilesProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [files, setFiles] = useState<FileNode[]>([]);
    const [openedFiles, setOpenedFiles] = useState<OpenedFile[]>([]);
    const [activeFile, setActiveFile] = useState<OpenedFile | null>(null);

    useEffect(() => {
        const fetchFiles = async () => {
            const { dirty_changes, file_index } = await getFileIndex()
            const fileIndex = file_index.map((file: FileNode) => ({ ...file }))
            setFiles(fileIndex)
        }
        fetchFiles()
    }, [setFiles])

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
            } else {
                setActiveFile(existingFile);
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


    const updateFileContent = useCallback((path: string, content: string) => {
        console.log({ openedFiles, path })
        setOpenedFiles(prev => prev.map(f =>
            f.node.path === path ? { ...f, content, isDirty: true } : f
        ));
    }, []);

    const saveActiveFile = useCallback(async () => {
        console.log('saving active file', { activeFile });
        if (activeFile) {
            await persistFile(activeFile.node.path, activeFile.content);
            setOpenedFiles(prev => prev.map(f =>
                f.node.path === activeFile.node.path ? { ...f, isDirty: false } : f
            ));
        }
    }, [activeFile, setOpenedFiles]);


    return (
        <FilesContext.Provider value={{
            files,
            openedFiles,
            openFile,
            closeFile,
            activeFile,
            setActiveFile,
            updateFileContent,
            saveActiveFile,
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