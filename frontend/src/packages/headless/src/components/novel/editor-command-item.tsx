import type { Editor, Range } from "@tiptap/core";
import { useCurrentEditor } from "@tiptap/react";
import { CommandEmpty, CommandItem } from "cmdk";
import { useAtomValue } from "jotai";
// @ts-nocheck
import { forwardRef } from "react";
import type { ComponentPropsWithoutRef } from "react";
import { rangeAtom } from "../../utils/atoms";

interface EditorCommandItemProps {
  readonly onCommand: ({
    editor,
    range,
  }: {
    editor: Editor;
    range: Range;
  }) => void;
}

export const EditorCommandItem = forwardRef<
  HTMLDivElement,
  EditorCommandItemProps & ComponentPropsWithoutRef<typeof CommandItem>
>(({ children, onCommand, ...rest }, ref) => {
  const { editor } = useCurrentEditor();
  const range = useAtomValue(rangeAtom);

  if (!editor || !range) return null;

  return (
    <CommandItem
      ref={ref}
      {...rest}
      onSelect={() => onCommand({ editor, range })}
    >
      {children}
    </CommandItem>
  );
});

EditorCommandItem.displayName = "EditorCommandItem";

export const EditorCommandEmpty = CommandEmpty;

export default EditorCommandItem;
