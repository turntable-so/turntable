import { Fragment, useEffect, useRef, useState } from "react";
import { Input } from "@/components/ui/input";
import { useLocalStorage } from "usehooks-ts";
import type { Command } from "@/components/editor/command-panel/command-panel-types";
import { LocalStorageKeys } from "@/app/constants/local-storage-keys";
import { getTopNCommands } from "@/components/editor/search-bar/get-top-n-commands";
import type {
  Item,
  Section,
  SectionType,
} from "@/components/editor/search-bar/types";
import { useCommandPanelContext } from "@/components/editor/command-panel/command-panel-context";
import { useFiles } from "@/app/contexts/FilesContext";

export default function SearchBar() {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  /*
   * File logic
   */
  const { searchFileIndex } = useFiles();
  const allFiles = searchFileIndex.map((file) => ({
   value: file.path,
   display: file.name
  }));
  // TODO make it the most recent 5
  const topFiles = allFiles.slice(0, 5);

  /*
   * Command logic
   */
  const { commandHistory, runCommandFromSearchBar } = useCommandPanelContext();
  const topCommands: Item[] = getTopNCommands({
    commandHistory,
    N: 5,
  });
  const allCommands = commandHistory.reduce((uniqueCommands, { command }) => {
    if (!uniqueCommands.some((item) => item.value === command)) {
      uniqueCommands.push({ value: command, display: command });
    }
    return uniqueCommands;
  }, [] as Item[]);

  /*
   * Define the sections
   */
  const sections: Section[] = [
    {
      title: "Files",
      topLevelItems: topFiles,
      allItems: allFiles,
      type: "file",
    },
    {
      title: "Commands",
      topLevelItems: topCommands,
      allItems: allCommands,
      type: "command",
    },
  ];

  const filteredSections = sections
    .map((section) => ({
      ...section,
      items: searchTerm
        ? section.allItems.filter((item) =>
            item.display.toLowerCase().includes(searchTerm.toLowerCase()),
          )
        : section.topLevelItems,
    }))
    .filter((section) => section.items.length > 0);

  const flatItems = filteredSections.flatMap((section) =>
    section.items.map((item) => ({
      sectionTitle: section.title,
      item,
      type: section.type,
    })),
  );

  const showDropDown =
    isOpen && filteredSections.some((section) => section.items.length > 0);

  const onFileClick = (value: string) => {};

  const onCommandClick = (value: string) => {
    runCommandFromSearchBar(value);
  };

  const actionMap: Record<SectionType, (item: Item) => void> = {
    file: (item) => onFileClick(item.value),
    command: (item) => onCommandClick(item.value),
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

            if (selectedItem.type === "file") {
              onFileClick(selectedItem.item.value);
            } else if (selectedItem.type === "command") {
              onCommandClick(selectedItem.item.value);
            }
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
    <div className="relative w-[40%]">
      <Input
        ref={inputRef}
        type="text"
        placeholder="Search & Commands (⌘P)"
        className="w-full bg-white"
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
      {showDropDown && (
        <div
          ref={dropdownRef}
          className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg overflow-hidden"
        >
          {flatItems.map((flatItem, index) => {
            const isFirstInSection =
              index === 0 ||
              flatItem.sectionTitle !== flatItems[index - 1].sectionTitle;

            return (
              <Fragment key={`${flatItem.sectionTitle}-${flatItem.item.value}`}>
                {isFirstInSection && (
                  <div className="px-4 py-2 font-semibold text-sm text-gray-600 border-t border-gray-300">
                    {flatItem.sectionTitle}
                  </div>
                )}
                <div
                  className={`px-4 py-2 cursor-pointer ${
                    index === selectedIndex
                      ? "bg-gray-100"
                      : "hover:bg-gray-100"
                  }`}
                  onMouseDown={() => {
                    setSearchTerm(flatItem.item.display);
                    setIsOpen(false);
                    actionMap[flatItem.type]?.(flatItem.item);
                  }}
                >
                  <span className={"text-sm font-medium"}>
                    {flatItem.type === "command" ? "dbt " : null}
                    {flatItem.item.display}
                  </span>{" "}
                  {flatItem.type === "command" ? (
                    <span className={"text-xs ml-1"}>Click to run</span>
                  ) : null}
                </div>
              </Fragment>
            );
          })}
        </div>
      )}
    </div>
  );
}
