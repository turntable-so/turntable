import { type FileNode, useFiles } from "@/app/contexts/FilesContext";
import { Input } from "@/components/ui/input";
import {
  type Dispatch,
  type SetStateAction,
  useEffect,
  useRef,
  useState,
} from "react";
import { useOnClickOutside } from "usehooks-ts";

interface FileExplorerProps {
  onClose: () => void;
  setContextFiles: Dispatch<SetStateAction<FileNode[]>>;
}

export default function FileExplorer({
  onClose,
  setContextFiles,
}: FileExplorerProps) {
  const { files } = useFiles();

  // State variable for search query
  const [searchQuery, setSearchQuery] = useState('');

  // Recursive function to collect matching files (unchanged)
  const collectMatchingFiles = (node: FileNode): FileNode[] => {
    let result: FileNode[] = [];

    const isMatchingFile =
      node.type === "file" &&
      (node.name.endsWith(".sql") ||
        node.name.endsWith(".yml") ||
        node.name.endsWith(".yaml"));

    if (isMatchingFile) {
      result.push(node);
    }

    if (node.children) {
      for (const child of node.children) {
        result = result.concat(collectMatchingFiles(child));
      }
    }

    return result;
  };

  const flatMap = files ? files.flatMap(collectMatchingFiles) : [];

  // Filtered files based on search query
  const filteredFiles = flatMap.filter((file) =>
    file.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const explorerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleClick = (e: React.MouseEvent, file: FileNode) => {
    e.stopPropagation();
    onClose();
    setContextFiles((prev) => {
      const isDuplicate = prev.some((f) => f.path === file.path);
      if (isDuplicate) return prev;
      return [...prev, file];
    });
  };

  const focusInputOnMount = () => {
    inputRef.current?.focus();
  };
  useEffect(focusInputOnMount, []);
  useOnClickOutside(explorerRef, onClose);

  return (
    <div
      ref={explorerRef}
      className="bg-white dark:bg-black rounded-md text-xs min-w-[250px]"
    >
      <Input
        ref={inputRef}
        type="text"
        placeholder="Search files by name"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="border-none focus:ring-0 focus:outline-none focus:border-none focus:ring-offset-0 focus-visible:ring-0 focus-visible:ring-offset-0"
      />
      <ul className="max-h-[40vh] overflow-y-auto">
        {filteredFiles.map((file) => (
          <li
            key={file.path}
            className="flex justify-between items-start py-1 cursor-pointer"
            onClick={(e) => handleClick(e, file)}
          >
            <span className="ml-2">{file.name}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
