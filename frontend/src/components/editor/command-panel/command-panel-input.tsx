import React, { useState, useEffect, useRef } from "react";
import { COMMAND_OPTIONS } from "./command-options";
import { CommandPanelState } from "./types";
import CommandPanelActionBtn from "./command-panel-action-btn";
import { type InputProps } from "@/components/ui/input";
import { cn } from "@/lib/utils";

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        className={cn(
          "flex h-10 w-full items-center rounded-md border border-input bg-white pl-3 text-sm ring-offset-background focus-within:ring-1 focus-within:ring-ring focus-within:ring-offset-2",
          className,
        )}
      >
        <p className="text-muted-foreground font-semibold">dbt</p>
        <input
          {...props}
          ref={ref}
          className="w-full p-2 placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50"
        />
      </div>
    );
  },
);

export default function CommandPanelInput() {
  const [commandPanelState, setCommandPanelState] = useState<CommandPanelState>("idling");
  const [inputValue, setInputValue] = useState<string>("");
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

  const fuzzyMatch = (input: string, option: string) => {
    let inputIndex = 0;
    let optionIndex = 0;

    input = input.toLowerCase();
    option = option.toLowerCase();

    while (inputIndex < input.length && optionIndex < option.length) {
      if (input[inputIndex] === option[optionIndex]) {
        inputIndex++;
      }
      optionIndex++;
    }

    return inputIndex === input.length;
  };

  const filteredOptions = COMMAND_OPTIONS.filter((option) => fuzzyMatch(inputValue, option));

  // Focus the input on mount
  useEffect(() => {
    const timer = setTimeout(() => {
      inputRef.current?.focus();
    }, 0);
    return () => clearTimeout(timer);
  }, []);

  // Close dropdown when clicking outside
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

  // Reset highlighted index when input value changes
  useEffect(() => {
    setHighlightedIndex(-1);
  }, [inputValue]);

  return (
    <div className="flex flex-row gap-2 relative items-center">
      <Input
        ref={inputRef}
        value={inputValue}
        onChange={(e) => {
          setInputValue(e.target.value);
          if (!isDropdownOpen) {
            setIsDropdownOpen(true);
          }
        }}
        onClick={handleInputClick}
        onKeyDown={(e) => {
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
            }
          }
        }}
      />
      {isDropdownOpen && (
        <div
          ref={dropdownRef}
          className="absolute top-full left-0 w-full bg-white border border-gray-300 rounded-md mt-1 z-10"
        >
          {filteredOptions.map((option, index) => (
            <div
              key={index}
              className={`p-2 cursor-pointer text-sm ${
                index === highlightedIndex ? "bg-gray-100" : "hover:bg-gray-100"
              }`}
              onMouseDown={(e) => {
                e.preventDefault(); // Prevent focus shift
                handleOptionClick(option);
              }}
              // Use onMouseEnter to update highlightedIndex when hovering
              onMouseEnter={() => setHighlightedIndex(index)}
            >
              {option}
            </div>
          ))}
        </div>
      )}
      <CommandPanelActionBtn commandPanelState={commandPanelState} inputValue={inputValue} />
    </div>
  );
}
