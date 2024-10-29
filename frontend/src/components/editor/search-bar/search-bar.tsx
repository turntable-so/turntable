import { useEffect, useRef, useState } from "react";
import { Input } from "@/components/ui/input";

interface Section {
  title: string;
  items: string[];
}

export default function SearchBar() {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const sections: Section[] = [
    { title: "Recent", items: ["Recent 1", "Recent 2", "Recent 3"] },
    { title: "Commands", items: ["Command 1", "Command 2", "Command 3"] },
    { title: "Files", items: ["File 1", "File 2", "File 3"] },
  ];

  const filteredSections = sections
    .map((section) => ({
      ...section,
      items: section.items.filter((item) =>
        item.toLowerCase().includes(searchTerm.toLowerCase())
      ),
    }))
    .filter((section) => section.items.length > 0);

  const flatItems = filteredSections.flatMap((section) =>
    section.items.map((item) => ({ sectionTitle: section.title, item }))
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
            prevIndex < flatItems.length - 1 ? prevIndex + 1 : prevIndex
          );
          break;
        case "ArrowUp":
          e.preventDefault();
          setSelectedIndex((prevIndex) =>
            prevIndex > 0 ? prevIndex - 1 : 0
          );
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
                      className={`px-4 py-2 cursor-pointer text-sm ${
                        itemCounter === selectedIndex
                          ? "bg-gray-100"
                          : "hover:bg-gray-100"
                      }`}
                      onMouseDown={() => {
                        setSearchTerm(item);
                        setIsOpen(false);
                      }}
                    >
                      {item}
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
