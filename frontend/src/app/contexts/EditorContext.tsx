import { createContext, useContext, useEffect, useState } from "react";
import { getBranch, cloneBranchAndMount } from "../actions/actions";

type EditorContextType = {
    branchId: string;
    branchName: string;
    readOnly: boolean | undefined;
    isCloned: boolean | undefined;
    fetchBranch: (branchId: string) => Promise<void>;
    cloneBranch: (branchId: string) => Promise<void>;
};

const EditorContext = createContext<EditorContextType>({
    branchId: "",
    branchName: "",
    readOnly: undefined,
    isCloned: undefined,
    fetchBranch: async () => { },
    cloneBranch: async () => { },
});

export const useEditor = () => {
    const context = useContext(EditorContext);
    if (context === undefined) {
        throw new Error("useEditor must be used within a EditorProvider");
    }
    return context;
}


export const EditorProvider = ({ children }: { children: React.ReactNode }) => {
    const [branchId, setBranchId] = useState("");
    const [branchName, setBranchName] = useState("");
    const [readOnly, setReadOnly] = useState<boolean | undefined>(undefined);
    const [isCloned, setIsCloned] = useState<boolean | undefined>(undefined);

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


    const contextValue = {
        branchId,
        branchName,
        readOnly,
        isCloned,
        fetchBranch,
        cloneBranch,
    }

    return <EditorContext.Provider value={contextValue}>{children}</EditorContext.Provider>;
};
