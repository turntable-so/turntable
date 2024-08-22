"use client";

import { X } from "lucide-react";
import * as React from "react";

import { Command as CommandPrimitive } from "cmdk";
import { Badge } from "./badge";
import {
    Command,
    CommandGroup,
    CommandItem,
    CommandList,
} from "./command";
import { ScrollArea } from "./scroll-area";

type Item = Record<"value" | "label", string>;

export function FancyMultiSelect({ items, selected, setSelected, label, functionSelected = null }: { items: Item[], selected: Item[], setSelected: any, label: string, functionSelected: any }) {
    const inputRef = React.useRef<HTMLInputElement>(null);
    const [open, setOpen] = React.useState(false);
    const [inputValue, setInputValue] = React.useState("");
    const [selectables, setSelectables] = React.useState([]);
    const handleUnselect = React.useCallback((item: Item) => {
        setSelected((prev: any) => prev.filter((s: any) => s.value !== item.value));
    }, [setSelected]);

    const handleKeyDown = React.useCallback(
        (e: React.KeyboardEvent<HTMLDivElement>) => {
            const input = inputRef.current;
            if (input) {
                if (e.key === "Delete" || e.key === "Backspace") {
                    if (input.value === "") {
                        if (functionSelected) {
                            const newSelected = [...selected];
                            newSelected.pop();
                            return functionSelected(newSelected);
                        }
                        setSelected((prev: Item[]) => {
                            const newSelected = [...prev];
                            newSelected.pop();
                            return newSelected;
                        });
                    }
                }
                // This is not a default behaviour of the <input /> field
                if (e.key === "Escape") {
                    input.blur();
                }
            }
        },
        []
    );


    React.useEffect(() => {
        {/* @ts-ignore */ }
        setSelectables(items.filter(
            (item) => !(selected.map(selectedItem => selectedItem.value).includes(item.value))
        )
        )
    }, [items, selected])


    return (
        <Command
            onKeyDown={handleKeyDown}
            className="overflow-visible bg-transparent"
        >
            <div className="group rounded-md border border-input px-1 py-1 text-sm ring-offset-background focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2">
                <div className="flex flex-wrap gap-1">
                    {selected.map((item) => {
                        return (
                            <Badge key={item.value} variant="secondary">
                                {item.label}
                                <button
                                    className="ml-1 rounded-full outline-none ring-offset-background focus:ring-2 focus:ring-ring focus:ring-offset-2"
                                    onKeyDown={(e) => {
                                        if (e.key === "Enter") {
                                            handleUnselect(item);
                                        }
                                    }}
                                    onMouseDown={(e) => {
                                        e.preventDefault();
                                        e.stopPropagation();
                                    }}
                                    onClick={() => handleUnselect(item)}
                                >
                                    <X className="h-3 w-3 text-muted-foreground hover:text-foreground" />
                                </button>
                            </Badge>
                        );
                    })}
                    {/* Avoid having the "Search" Icon */}
                    <CommandPrimitive.Input
                        ref={inputRef}
                        value={inputValue}
                        onValueChange={setInputValue}
                        onBlur={() => setOpen(false)}
                        onFocus={() => setOpen(true)}
                        placeholder={label}
                        className="ml-2 flex-1 bg-transparent outline-none placeholder:text-muted-foreground"
                    />
                </div>
            </div>
            <div className="relative mt-2">
                <CommandList>
                    {open && selectables.length > 0 ? (
                        <div className="absolute top-0 z-10 w-full rounded-md border bg-popover text-popover-foreground shadow-md outline-none animate-in">
                            <ScrollArea>
                                <CommandGroup className="max-h-[400px] overflow-auto">
                                    {selectables.map((item: any) => {
                                        return (
                                            <CommandItem
                                                key={item.value as any}
                                                onMouseDown={(e) => {
                                                    e.preventDefault();
                                                    e.stopPropagation();
                                                }}
                                                onSelect={(item) => {
                                                    setInputValue("");
                                                    if (functionSelected) {
                                                        const newSelected = [...selected, item];
                                                        return functionSelected(newSelected);
                                                    }
                                                    setSelected((prev: any) => [...prev, item]);
                                                }}
                                                className={"cursor-pointer"}
                                            >
                                                {item.label}
                                            </CommandItem>
                                        );
                                    })}
                                </CommandGroup>
                            </ScrollArea>
                        </div>
                    ) : null}
                </CommandList>
            </div >
        </Command >
    );
}