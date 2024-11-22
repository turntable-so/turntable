import { useFieldArray } from "react-hook-form";
import { DndProvider, useDrag, useDrop } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { GripVertical, Trash2, Plus } from "lucide-react";
import { useEffect } from "react";
import { cn } from "@/lib/utils";
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
interface CommandItemProps {
    command: string;
    index: number;
    moveCommand: (dragIndex: number, hoverIndex: number) => void;
    onDelete: () => void;
    onChange: (value: string) => void;
}

const CommandItem = ({ command, index, moveCommand, onDelete, onChange }: CommandItemProps) => {
    const [{ isDragging }, drag, dragPreview] = useDrag({
        type: "COMMAND",
        item: { index },
        collect: (monitor) => ({
            isDragging: monitor.isDragging(),
        }),
    });

    const [, drop] = useDrop({
        accept: "COMMAND",
        hover(item: { index: number }) {
            if (item.index !== index) {
                moveCommand(item.index, index);
                item.index = index;
            }
        },
    });

    return (
        <div
            ref={(node) => dragPreview(drop(node))}
            className={cn(
                "flex items-center space-x-2 p-2 border rounded-md",
                isDragging ? "opacity-50" : ""
            )}
        >
            <div ref={drag} className="cursor-move">
                <GripVertical className="h-4 w-4 text-gray-400" />
            </div>
            <Input
                value={command}
                onChange={(e) => onChange(e.target.value)}
                placeholder="Enter command..."
                className="flex-1"
            />
            <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={onDelete}
            >
                <Trash2 className="h-4 w-4" />
            </Button>
        </div>
    );
};

export const CommandList = ({ form }: { form: any }) => {
    const { fields, append, remove, move } = useFieldArray({
        control: form.control,
        name: "commands",
    });

    useEffect(() => {
        if (fields.length === 0) {
            append("dbt build");
        }
    }, [fields.length, append]);

    const handleAddCommand = () => {
        append("");
    };

    return (
        <DndProvider backend={HTML5Backend}>
            <FormField
                control={form.control}
                name="commands"
                render={() => (
                    <FormItem>
                        <FormLabel>Commands</FormLabel>
                        <FormControl>
                            <div className="space-y-2">
                                {fields.map((field, index) => (
                                    <CommandItem
                                        key={field.id}
                                        command={form.watch(`commands.${index}`)}
                                        index={index}
                                        moveCommand={move}
                                        onDelete={() => remove(index)}
                                        onChange={(value) => {
                                            form.setValue(`commands.${index}`, value);
                                        }}
                                    />
                                ))}
                                <Button
                                    type="button"
                                    variant="outline"
                                    size="sm"
                                    onClick={handleAddCommand}
                                    className="w-full"
                                >
                                    <Plus className="h-4 w-4 mr-2" />
                                    Add Command
                                </Button>
                            </div>
                        </FormControl>
                        <FormMessage />
                    </FormItem>
                )}
            />
        </DndProvider>
    );
}; 