import { MAX_RECENT_COMMANDS, useFiles } from "@/app/contexts/FilesContext";
import type {
    FileSection,
    FileValue,
    FilteredSection,
    FlatItem,
    Item,
} from "@/components/editor/search-bar/types";
import { Input } from "@/components/ui/input";
import { Fragment, useEffect, useRef, useState } from "react";
import { getIcon } from "../icons";

export default function InlineTabSearch() {
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedIndex, setSelectedIndex] = useState(-1);
    const dropdownRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    /*
     * File logic
     */
    const { searchFileIndex, openFile, recentFiles, activeFile } = useFiles();
    const allFiles: Array<Item<FileValue>> = searchFileIndex.map((file) => ({
        value: {
            path: file.path,
            name: file.name,
        },
        display: file.name,
    }));
    const topFiles = recentFiles.map((file) => ({
        value: {
            path: file.path,
            name: file.name,
        },
        display: file.name,
    }));


    const sections = [
        {
            title: "Files",
            topLevelItems:
                topFiles.length >= 2
                    ? topFiles
                    : allFiles.slice(0, MAX_RECENT_COMMANDS),
            allItems: allFiles,
            type: "file",
        } as FileSection,
    ];

    const filteredSections: FilteredSection[] = sections
        .map((section) => {
            const items = searchTerm
                ? section.allItems.filter((item) => {
                    const itemDisplay = item.display.toLowerCase();
                    const search = searchTerm.toLowerCase();

                    return itemDisplay.includes(search);
                })
                : section.topLevelItems;

            return {
                title: section.title,
                items,
                type: section.type,
            } as FilteredSection;
        })
        .filter((section) => section.items.length > 0);

    const flatItems: FlatItem[] = filteredSections.flatMap((section) =>
        section.items.map((item) => ({
            sectionTitle: section.title,
            item,
            type: section.type,
        })),
    );

    const resetState = () => {
        setIsOpen(false);
        setSearchTerm("");
        setSelectedIndex(-1);
        inputRef.current?.blur();
    };

    const onFileClick = (item: FileValue) => {
        openFile({
            type: "file",
            name: item.name,
            path: item.path,
        });
        resetState();
    };


    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.metaKey || e.ctrlKey) && e.key === "p") {
                e.preventDefault();
                inputRef.current?.focus();
                setIsOpen(true);
                setSelectedIndex(flatItems.length > 0 ? 0 : -1);
                return;
            }

            if (!isOpen) {
                return;
            }

            switch (e.key) {
                case "ArrowDown":
                    e.preventDefault();
                    setSelectedIndex((prevIndex) =>
                        prevIndex < flatItems.length - 1 ? prevIndex + 1 : prevIndex,
                    );
                    break;
                case "ArrowUp":
                    e.preventDefault();
                    setSelectedIndex((prevIndex) => (prevIndex > 0 ? prevIndex - 1 : 0));
                    break;
                case "Enter":
                    if (selectedIndex >= 0) {
                        const selectedItem = flatItems[selectedIndex];
                        setSearchTerm(selectedItem.item.display);
                        setIsOpen(false);
                        onFileClick(selectedItem.item.value as FileValue);

                    }
                    break;
                case "Escape":
                    e.preventDefault();
                    setIsOpen(false);
                    setSearchTerm("");
                    inputRef.current?.blur();
                    break;
            }
        };

        document.addEventListener("keydown", handleKeyDown);
        return () => {
            document.removeEventListener("keydown", handleKeyDown);
        };
    }, [isOpen, selectedIndex, flatItems]);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (
                dropdownRef.current &&
                !dropdownRef.current.contains(event.target as Node) &&
                inputRef.current &&
                !inputRef.current.contains(event.target as Node)
            ) {
                setIsOpen(false);
            }
        };

        if (isOpen) {
            document.addEventListener("mousedown", handleClickOutside);
        } else {
            setSelectedIndex(-1);
            document.removeEventListener("mousedown", handleClickOutside);
        }

        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [isOpen]);

    return (
        <div className="w-full max-w-2xl">
            <Input
                ref={inputRef}
                type="text"
                placeholder="Search files"
                autoFocus
                className="w-full bg-muted dark:bg-zinc-900"
                value={searchTerm}
                onChange={(e) => {
                    setSearchTerm(e.target.value);
                    setIsOpen(true);
                    setSelectedIndex(flatItems.length > 0 ? 0 : -1);
                }}
                onFocus={() => {
                    setIsOpen(true);
                    setSelectedIndex(flatItems.length > 0 ? 0 : -1);
                }}
            />
            <div
                className="z-10 w-full mt-1 bg-white dark:bg-zinc-900"
            >
                {flatItems.length === 0 ? (
                    <div className="px-4 py-2 text-sm text-gray-600">No files found</div>
                ) : (
                    flatItems.map((flatItem, index) => {
                        const isFirstInSection =
                            index === 0 ||
                            flatItem.sectionTitle !== flatItems[index - 1].sectionTitle;

                        return (
                            <Fragment
                                key={`${flatItem.sectionTitle}-${JSON.stringify(flatItem.item.value)}-${index}`}
                            >
                                {isFirstInSection && (
                                    <div className="px-4 py-2 font-semibold text-sm text-gray-600   border-gray-300">
                                        {flatItem.sectionTitle}
                                    </div>
                                )}
                                <div
                                    className={`px-4 py-2 cursor-pointer ${index === selectedIndex
                                        ? "bg-gray-100 dark:bg-zinc-800"
                                        : "hover:bg-gray-100 dark:hover:bg-zinc-800"
                                        }`}
                                    onMouseDown={() => {
                                        setSearchTerm(flatItem.item.display);
                                        setIsOpen(false);

                                        onFileClick(flatItem.item.value as FileValue);

                                    }}
                                >
                                    <span
                                        className={"text-sm font-medium flex gap-2 items-center"}
                                    >
                                        {flatItem.type === "file" && getIcon(flatItem.item.value)}
                                        {flatItem.item.display}
                                    </span>
                                </div>
                            </Fragment>
                        );
                    })
                )}
            </div>
        </div>
    );
}
