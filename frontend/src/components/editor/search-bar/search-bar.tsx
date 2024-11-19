import { MAX_RECENT_COMMANDS, useFiles } from "@/app/contexts/FilesContext";
import { useCommandPanelContext } from "@/components/editor/command-panel/command-panel-context";
import { getTopNCommands } from "@/components/editor/search-bar/get-top-n-commands";
import type {
  CommandSection,
  CommandValue,
  FileSection,
  FileValue,
  FilteredSection,
  FlatItem,
  Item,
} from "@/components/editor/search-bar/types";
import { Input } from "@/components/ui/input";
import { Fragment, useEffect, useRef, useState } from "react";
import { getIcon } from "../icons";

export default function SearchBar() {
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

  /*
   * Command logic
   */
  const { commandHistory, runCommandFromSearchBar } = useCommandPanelContext();
  const [topCommands, setTopCommands] = useState<Array<Item<CommandValue>>>([]);

  useEffect(() => {
    if (!activeFile) {
      return;
    }

    const modelSplit = activeFile.node.name.split(".");
    const modelName = modelSplit[0];
    const modelFileType = modelSplit[1];
    if (modelFileType !== "sql") {
      setTopCommands(
        getTopNCommands({
          commandHistory,
          N: 5,
        }),
      );
      return;
    }

    const commandTypes = ["build", "run", "test"];
    const selectPatterns = [
      { pattern: `${modelName}`, label: "model" },
      { pattern: `${modelName}+`, label: "model+ (Downstream)" },
      { pattern: `+${modelName}`, label: "+model (Upstream)" },
      { pattern: `+${modelName}+`, label: "+model+ (Up/downstream)" },
    ];

    const capitalize = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

    setTopCommands(
      commandTypes.flatMap((commandType) =>
        selectPatterns.map(({ pattern, label }) => ({
          value: `${commandType} --select ${pattern}`,
          display: `${capitalize(commandType)} ${label}`,
        })),
      ),
    );
  }, [activeFile]);

  const allCommands = [
    ...topCommands,
    ...commandHistory.reduce((uniqueCommands, { command }) => {
      if (
        !uniqueCommands.some((item) => item.value === command) &&
        !topCommands.some((topItem) => topItem.value === command)
      ) {
        uniqueCommands.push({ value: command, display: command });
      }
      return uniqueCommands;
    }, [] as Item<CommandValue>[]),
  ];

  /*
   * Define the sections
   */
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
    {
      title: "Commands",
      topLevelItems: topCommands,
      allItems: allCommands,
      type: "command",
    } as CommandSection,
  ];

  const filteredSections: FilteredSection[] = sections
    .map((section) => {
      const items = searchTerm
        ? section.allItems.filter((item) => {
            const itemDisplay = item.display.toLowerCase();
            const search = searchTerm.toLowerCase();

            // For commands, also check if the full command (e.g. "dbt run") matches
            if (section.type === "command" && typeof item.value === "string") {
              return (
                itemDisplay.includes(search) ||
                item.value.toLowerCase().includes(search)
              );
            }

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

  const showDropDown =
    isOpen && filteredSections.some((section) => section.items.length > 0);

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

  const onCommandClick = (item: CommandValue) => {
    runCommandFromSearchBar(item);
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

            if (selectedItem.type === "file") {
              onFileClick(selectedItem.item.value as FileValue);
            } else if (selectedItem.type === "command") {
              onCommandClick(selectedItem.item.value as CommandValue);
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
        className="w-full bg-white dark:bg-zinc-900"
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
          className="absolute z-10 w-full mt-1 bg-white dark:bg-zinc-900 border border-gray-300 dark:border-zinc-700 rounded-md shadow-lg overflow-hidden"
        >
          {flatItems.map((flatItem, index) => {
            const isFirstInSection =
              index === 0 ||
              flatItem.sectionTitle !== flatItems[index - 1].sectionTitle;

            return (
              <Fragment
                key={`${flatItem.sectionTitle}-${JSON.stringify(flatItem.item.value)}-${index}`}
              >
                {isFirstInSection && (
                  <div className="px-4 py-2 font-semibold text-sm text-gray-600 border-t border-gray-300">
                    {flatItem.sectionTitle}
                  </div>
                )}
                <div
                  className={`px-4 py-2 cursor-pointer ${
                    index === selectedIndex
                      ? "bg-gray-100 dark:bg-zinc-800"
                      : "hover:bg-gray-100 dark:hover:bg-zinc-800"
                  }`}
                  onMouseDown={() => {
                    setSearchTerm(flatItem.item.display);
                    setIsOpen(false);

                    if (flatItem.type === "file") {
                      onFileClick(flatItem.item.value as FileValue);
                    } else if (flatItem.type === "command") {
                      onCommandClick(flatItem.item.value as CommandValue);
                    }
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
          })}
        </div>
      )}
    </div>
  );
}
