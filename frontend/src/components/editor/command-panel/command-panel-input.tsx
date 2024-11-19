import { useCommandPanelContext } from "@/components/editor/command-panel/command-panel-context";
import React, { useEffect, useRef, useState } from "react";
import CommandInput from "./command-input";
import { getCommandOptions } from "./command-panel-options";
import { useFiles } from "@/app/contexts/FilesContext";

export default function CommandPanelInput() {
  const { branchId } = useFiles();
  const {
    inputValue,
    setInputValue,
    commandOptions,
    setCommandOptions,
    runCommand,
  } = useCommandPanelContext();
  const [isDropdownOpen, setIsDropdownOpen] = useState<boolean>(false);
  const [highlightedIndex, setHighlightedIndex] = useState<number>(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleInputClick = () => {
    setIsDropdownOpen(true);
  };

  const handleOptionClick = (option: string) => {
    setInputValue(option);
    setIsDropdownOpen(false);
    setHighlightedIndex(-1);
  };

  const handleCommandExecution = () => {
    setInputValue("");
    setIsDropdownOpen(false);
    setHighlightedIndex(-1);
    runCommand();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setIsDropdownOpen(true);
      setHighlightedIndex((prevIndex) => {
        const nextIndex = prevIndex + 1;
        return nextIndex < filteredOptions.length ? nextIndex : 0;
      });
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setIsDropdownOpen(true);
      setHighlightedIndex((prevIndex) => {
        const nextIndex = prevIndex - 1;
        return nextIndex >= 0 ? nextIndex : filteredOptions.length - 1;
      });
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (highlightedIndex >= 0 && highlightedIndex < filteredOptions.length) {
        handleOptionClick(filteredOptions[highlightedIndex]);
      } else {
        handleCommandExecution();
      }
    }
  };

  const fuzzyMatch = (input: string, option: string) => {
    let inputIndex = 0;
    let optionIndex = 0;

    const cleanedInput = input.toLowerCase();
    const cleanedOption = option.toLowerCase();

    while (
      inputIndex < cleanedInput.length &&
      optionIndex < cleanedOption.length
    ) {
      if (cleanedInput[inputIndex] === cleanedOption[optionIndex]) {
        inputIndex++;
      }
      optionIndex++;
    }

    return inputIndex === cleanedInput.length;
  };

  const filteredOptions = commandOptions.filter((option) =>
    fuzzyMatch(inputValue, option),
  );

  useEffect(() => {
    const timer = setTimeout(() => {
      inputRef.current?.focus();
    }, 0);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  useEffect(() => {
    setHighlightedIndex(-1);
  }, [inputValue]);

  useEffect(() => {
    setCommandOptions(getCommandOptions(branchId));
  }, []);

  return (
    <div className="flex flex-row gap-2 relative items-center">
      <CommandInput
        ref={inputRef}
        value={inputValue}
        onChange={(e) => {
          setInputValue(e.target.value);
          if (!isDropdownOpen) {
            setIsDropdownOpen(true);
          }
        }}
        onClick={handleInputClick}
        onKeyDown={handleKeyDown}
      />
      {isDropdownOpen && (
        <div
          ref={dropdownRef}
          className="absolute top-full left-0 w-1/3 bg-white dark:bg-zinc-950 border border-gray-300 dark:border-zinc-700 rounded-md mt-1 z-10"
        >
          {filteredOptions.map((option, index) => (
            <div
              key={option}
              className={`py-2 px-4 cursor-pointer text-sm ${
                index === highlightedIndex
                  ? "bg-gray-100 dark:bg-zinc-700"
                  : "hover:bg-gray-100 dark:hover:bg-zinc-700"
              }`}
              onMouseDown={(e) => {
                e.preventDefault();
                handleOptionClick(option);
              }}
              onMouseEnter={() => setHighlightedIndex(index)}
            >
              {option}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
