import { useEffect, useRef, useState } from "react";
import { Input } from "@/components/ui/input";
import { useLocalStorage } from "usehooks-ts";
import type { Command } from "@/components/editor/command-panel/command-panel-types";
import { LocalStorageKeys } from "@/app/constants/local-storage-keys";
import { getTopNCommands } from "@/components/editor/search-bar/get-top-n-commands";
import type { Section } from "@/components/editor/search-bar/types";

export default function SearchBar() {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [commandHistory, _] = useLocalStorage<Command[]>(
    LocalStorageKeys.commandHistory,
    [],
  );

  const topCommands = getTopNCommands({
    commandHistory,
    N: 5,
  });
  const allCommands = Array.from(new Set(commandHistory.map(({ command }) => command)));

  const sections: Section[] = [
    { title: "Files", topLevelItems: ["Wow"], allItems: ["Wow", "Panda", "ls"], type: "file" },
    {
      title: "Commands",
      topLevelItems: topCommands,
      allItems: allCommands,
      type: "command",
    },
  ];

  // Adjusted code starts here
  const filteredSections = sections
    .map((section) => ({
      ...section,
      // Use 'topLevelItems' when searchTerm is empty, otherwise filter 'allItems'
      items: searchTerm
        ? section.allItems.filter((item) =>
            item.toLowerCase().includes(searchTerm.toLowerCase()),
          )
        : section.topLevelItems,
    }))
    .filter((section) => section.items.length > 0);

  const flatItems = filteredSections.flatMap((section) =>
    section.items.map((item) => ({ sectionTitle: section.title, item })),
  );

  const showDropDown =
    isOpen && filteredSections.some((section) => section.items.length > 0);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "p") {
        e.preventDefault();
        inputRef.current?.focus();
        setIsOpen(true);
        setSelectedIndex(flatItems.length > 0 ? 0 : -1);
        return;
      }

      if (!isOpen) return;

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
            setSearchTerm(selectedItem.item);
            setIsOpen(false);
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

  // Handle clicks outside the component
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
    <div className="relative w-1/3">
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
          {(() => {
            let itemCounter = -1;
            return filteredSections.map((section) => (
              <div key={section.title}>
                <div className="px-4 py-2 font-semibold text-sm text-gray-600 border-t border-gray-300">
                  {section.title}
                </div>
                {section.items.map((item) => {
                  itemCounter++;
                  return (
                    <div
                      key={item}
                      className={`px-4 py-2 cursor-pointer ${
                        itemCounter === selectedIndex
                          ? "bg-gray-100"
                          : "hover:bg-gray-100"
                      }`}
                      onMouseDown={() => {
                        setSearchTerm(item);
                        setIsOpen(false);
                      }}
                    >
                      <span className={"text-sm font-medium"}>{item}</span>{" "}
                      {section.type === "command" ? (
                        <span className={"text-xs ml-1"}>Click to run</span>
                      ) : null}
                    </div>
                  );
                })}
              </div>
            ));
          })()}
        </div>
      )}
    </div>
  );
}
