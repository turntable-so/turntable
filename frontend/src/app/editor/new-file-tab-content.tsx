import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Database, FileText, Plus } from "lucide-react";
import { useEffect, useRef, useState, KeyboardEvent } from "react";
import { useFiles } from "../contexts/FilesContext";

export default function NewFileTabContent() {
    const inputRef = useRef<HTMLInputElement>(null);
    const [selectionIndex, setSelectionIndex] = useState(0);
    const [searchQuery, setSearchQuery] = useState('');

    const { searchFileIndex, createNewQueryTab } = useFiles();

    useEffect(() => {
        if (inputRef.current) {
            inputRef.current.focus();
        }
    }, []);

    const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'ArrowUp') {
            event.preventDefault();
            setSelectionIndex((prevIndex) =>
                prevIndex === 0 ? searchFileIndex.length + 1 : prevIndex - 1
            );
        } else if (event.key === 'ArrowDown') {
            event.preventDefault();
            setSelectionIndex((prevIndex) =>
                (prevIndex + 1) % (searchFileIndex.length + 2)
            );
        }
    };

    return (
        <div className='w-full flex justify-center'>
            <div className='w-full max-w-2xl'>
                <Input
                    ref={inputRef}
                    value={searchQuery}
                    onChange={(e) => {
                        setSelectionIndex(0);
                        setSearchQuery(e.target.value);
                    }}
                    className='bg-muted w-full flex border-none focus:ring-0 focus:ring-border-0 focus:border-transparent'
                    placeholder='Search for files, assets & tools'
                    onKeyDown={handleKeyDown}
                />
                <div className='px-2 flex gap-2 flex-col py-4'>
                    <div onClick={createNewQueryTab} className={`hover:cursor-pointer hover:bg-gray-200 rounded py-1 flex gap-2 items-center ${selectionIndex === 0 ? 'bg-muted' : ''}`}>
                        <Database className="w-4 h-4" />
                        New query
                    </div>
                    <div className={`flex gap-2 items-center ${selectionIndex === 1 ? 'bg-muted' : ''}`}>
                        <Plus className="w-4 h-4" />
                        New file
                    </div>
                </div>
                <Separator className='my-2' />
                <div className='px-2 text-sm text-muted-foreground'>
                    Files
                </div>
                <div>
                    {searchFileIndex.filter((file) => file.type === 'file' && file.name.includes(searchQuery)).slice(0, 10).map((file, index) => (
                        <div key={file.path} className={`px-2 py-1 ${selectionIndex === index + 2 ? 'bg-muted' : ''}`}>
                            {file.name}
                        </div>
                    ))}
                </div>
            </div>
        </div >
    )
}