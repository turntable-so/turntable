"use client";

import { type OpenedFile, useFiles } from "@/app/contexts/FilesContext";
import { useLayoutContext } from "@/app/contexts/LayoutContext";
import CustomDiffEditor from "@/components/editor/CustomDiffEditor";
import CustomEditor from "@/components/editor/CustomEditor";
import InlineTabSearch from "@/components/editor/search-bar/inline-tab-search";
import { Button } from "@/components/ui/button";
import { CircleCheck, CircleSlash, Download, Loader2 } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useRef } from "react";
import { useAISidebar } from "./ai/ai-sidebar-context";

export default function EditorContent({
  containerWidth,
}: { containerWidth: number }) {
  const { setAiCustomSelections } = useAISidebar();
  const { sidebarRightShown, setSidebarRightShown } = useLayoutContext();
  const { resolvedTheme } = useTheme();
  const {
    activeFile,
    updateFileContent,
    saveFile,
    setActiveFile,
    isCloning,
    downloadFile,
    runQueryPreview,
    compileActiveFile,
    isApplying,
  } = useFiles();

  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);
  const addToChatButtonRef = useRef<HTMLElement | null>(null);
  const editorDomNodeRef = useRef<HTMLElement | null>(null);

  // We'll keep a reference to the "Add To Chat" button here
  let addToChatButton: HTMLElement | null = null;
  let editorDomNode: HTMLElement | null = null;

  // Define your custom theme
  const customTheme = {
    base: resolvedTheme === "dark" ? "vs-dark" : "vs",
    inherit: true,
    rules: [],
  };

  const addToChat = (
    selectedText: string,
    startLine: number,
    endLine: number,
    fileName: string,
  ) => {
    setAiCustomSelections((prev) => [
      ...(prev || []),
      {
        selection: selectedText,
        start_line: startLine,
        end_line: endLine,
        file_name: fileName,
      },
    ]);
    if (!sidebarRightShown) {
      setSidebarRightShown(true);
    }
  };

  useEffect(() => {
    if (monacoRef.current) {
      monacoRef.current.editor.defineTheme("mutedTheme", {
        ...customTheme,
        colors: {
          ...customTheme.colors,
        },
      });
      monacoRef.current.editor.setTheme("mutedTheme");
    }
  }, [resolvedTheme]);

  const removeAddToChatButton = () => {
    if (addToChatButtonRef.current) {
      document.body.removeChild(addToChatButtonRef.current);
      addToChatButtonRef.current = null;
    }
  };

  // Handle global clicks outside the editor or the button to remove the AddToChat button
  const handleGlobalClick = (event: MouseEvent) => {
    if (addToChatButtonRef.current) {
      const target = event.target as HTMLElement;
      const clickedInsideButton = addToChatButtonRef.current.contains(target);
      const clickedInsideEditor =
        editorDomNodeRef.current && editorDomNodeRef.current.contains(target);
      if (!clickedInsideButton && !clickedInsideEditor) {
        removeAddToChatButton();
      }
    }
  };

  useEffect(() => {
    document.addEventListener("click", handleGlobalClick);
    return () => {
      document.removeEventListener("click", handleGlobalClick);
    };
  }, []);

  if (activeFile?.node?.type === "error") {
    if (activeFile.content === "FILE_EXCEEDS_SIZE_LIMIT") {
      return (
        <div className="h-full w-full flex flex-col gap-4 items-center justify-center">
          <div>
            This file is too large to open. Please download the file instead.
          </div>
          <Button onClick={() => downloadFile(activeFile.node.path)}>
            <Download className="mr-2 h-4 w-4" />
            Download
          </Button>
        </div>
      );
    }
    return (
      <div className="h-full w-full flex items-center justify-center">
        {activeFile.content}
      </div>
    );
  }

  if (activeFile?.node?.type === "loader") {
    return (
      <div className="h-full w-full flex items-center justify-center">
        <Loader2 className="h-4 w-4 animate-spin" />
      </div>
    );
  }

  if (
    activeFile?.node?.type === "url" &&
    typeof activeFile.content === "string"
  ) {
    return (
      <iframe
        src={activeFile.content}
        title={activeFile.node.name}
        width="100%"
        height="100%"
      />
    );
  }

  if (activeFile?.view === "diff") {
    return (
      <CustomDiffEditor
        text-muted-foreground
        original={activeFile?.diff?.original || ""}
        modified={activeFile?.diff?.modified || ""}
        width={containerWidth - 2}
        language="sql"
        options={{
          minimap: { enabled: false },
          scrollbar: {
            vertical: "visible",
            horizontal: "visible",
            verticalScrollbarSize: 8,
            horizontalScrollbarSize: 8,
            verticalSliderSize: 8,
            horizontalSliderSize: 8,
          },
          lineNumbers: "on",
          wordWrap: "on",
          fontSize: 14,
          lineNumbersMinChars: 3,
        }}
        theme="mutedTheme"
      />
    );
  }

  if (activeFile?.view === "apply") {
    const onCancel = () => {
      setActiveFile({
        ...activeFile,
        view: "edit",
        diff: undefined,
      });
    };

    const onApply = () => {
      setActiveFile(
        (prev) =>
          ({
            ...prev,
            view: "edit",
            content: activeFile?.diff?.modified,
            diff: undefined,
          }) as OpenedFile,
      );
      saveFile(activeFile?.node.path || "", activeFile?.diff?.modified || "");
    };

    return (
      <div className="h-full w-full flex flex-col items-center justify-center">
        <div className="flex gap-2 justify-end w-full my-1">
          <Button
            size="sm"
            variant="outline"
            onClick={onCancel}
            disabled={isApplying}
          >
            <CircleSlash className="mr-2 h-4 w-4" />
            Cancel
          </Button>
          <Button size="sm" onClick={onApply} disabled={isApplying}>
            <CircleCheck className="mr-2 h-4 w-4" />
            Apply
          </Button>
        </div>
        <CustomDiffEditor
          original={activeFile?.diff?.original || ""}
          modified={activeFile?.diff?.modified || ""}
          width={containerWidth - 2}
          language="sql"
          options={{
            minimap: { enabled: false },
            scrollbar: {
              vertical: "visible",
              horizontal: "visible",
              verticalScrollbarSize: 8,
              horizontalScrollbarSize: 8,
              verticalSliderSize: 8,
              horizontalSliderSize: 8,
            },
            lineNumbers: "on",
            wordWrap: "on",
            fontSize: 14,
            lineNumbersMinChars: 3,
          }}
          theme="mutedTheme"
        />
      </div>
    );
  }

  if (activeFile?.view === "new") {
    return (
      <div className="h-full w-full flex justify-center text-muted-foreground dark:bg-black bg-white">
        {isCloning ? (
          <div className="flex items-center space-x-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            <div>Setting up environment</div>
          </div>
        ) : (
          <div className="w-full h-full flex pt-10 justify-center">
            <InlineTabSearch />
          </div>
        )}
      </div>
    );
  }

  const getLanguage = (activeFile: OpenedFile) => {
    if (activeFile.node?.path.endsWith(".sql")) {
      return "sql";
    }
    if (
      activeFile.node?.path.endsWith(".yml") ||
      activeFile.node?.path.endsWith(".yaml")
    ) {
      return "yaml";
    }
    if (activeFile.node?.path.endsWith(".md")) {
      return "markdown";
    }
    if (activeFile.node?.path.endsWith(".json")) {
      return "javascript";
    }
    return "sql";
  };

  return (
    <CustomEditor
      key={activeFile?.node.path}
      value={typeof activeFile?.content === "string" ? activeFile.content : ""}
      onChange={(value) => {
        if (activeFile) {
          updateFileContent(activeFile.node.path, value || "");
          setActiveFile({
            ...activeFile,
            content: value || "",
          });
        }
      }}
      language={activeFile ? getLanguage(activeFile) : "sql"}
      options={{
        minimap: { enabled: false },
        scrollbar: {
          vertical: "visible",
          horizontal: "visible",
          verticalScrollbarSize: 8,
          horizontalScrollbarSize: 8,
          verticalSliderSize: 8,
          horizontalSliderSize: 8,
        },
        lineNumbers: "on",
        wordWrap: "on",
        fontSize: 14,
        lineNumbersMinChars: 3,
        renderLineHighlight: "none",
      }}
      width={containerWidth - 2}
      onMount={(editor, monaco) => {
        editorRef.current = editor;
        monacoRef.current = monaco;

        editor.updateOptions({ theme: "mutedTheme" });

        // Store the editor DOM node for global click checks
        editorDomNode = editor.getDomNode() as HTMLElement;

        // Prevent default behavior for cmd+s
        editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
          saveFile(activeFile?.node.path || "", editor.getValue());
        });

        // Run query with cmd+Enter
        editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () =>
          runQueryPreview(editor.getValue()),
        );

        // Compile active file with cmd+shift+Enter
        editor.addCommand(
          monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.Enter,
          () => compileActiveFile(activeFile?.node.name || ""),
        );

        editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyL, () => {
          const selection = editor.getSelection();
          if (selection && !selection.isEmpty()) {
            const selectedText = editor.getModel()?.getValueInRange(selection);
            addToChat(
              selectedText,
              selection.startLineNumber,
              selection.endLineNumber,
              activeFile?.node.name || "",
            );
          }
        });

        editor.onMouseUp((e) => {
          const selection = editor.getSelection();
          const model = editor.getModel();

          if (selection && !selection.isEmpty()) {
            const position = selection.getStartPosition();
            const pixelPosition = editor.getScrolledVisiblePosition(position);
            if (!pixelPosition) {
              return;
            }

            // Remove any existing button
            removeAddToChatButton();

            // Get the editor's DOM node and its position on the page
            const editorRect = editorDomNode.getBoundingClientRect();

            // Calculate absolute position of the start of selection
            const absoluteLeft =
              editorRect.left + pixelPosition.left - editor.getScrollLeft();
            const absoluteTop =
              editorRect.top + pixelPosition.top - editor.getScrollTop();

            addToChatButton = document.createElement("button");
            addToChatButton.textContent = "Add to Chat (⌘L)";
            addToChatButton.className = "add-to-chat-button";
            addToChatButton.style.position = "absolute";
            addToChatButton.style.left = `${absoluteLeft}px`;
            addToChatButton.style.top = `${absoluteTop}px`;
            addToChatButton.style.transform = "translate(-50%, -100%)";
            addToChatButton.style.zIndex = "1000";
            addToChatButtonRef.current = addToChatButton;

            addToChatButton.onclick = (event) => {
              event.stopPropagation();
              const selection = editor.getSelection();
              const model = editor.getModel();
              if (selection && model) {
                const selectedText = model.getValueInRange(selection);
                const startLine = selection.startLineNumber;
                const endLine = selection.endLineNumber;
                const fileName = activeFile?.node.name || "";

                addToChat(selectedText, startLine, endLine, fileName);
                removeAddToChatButton();

                editor.setPosition(selection.getEndPosition());
                editor.setSelection(
                  new monaco.Selection(
                    selection.endLineNumber,
                    selection.endColumn,
                    selection.endLineNumber,
                    selection.endColumn,
                  ),
                );
              }
            };

            // Append the button to the body
            document.body.appendChild(addToChatButton);
          } else {
            // Remove the button if selection is empty
            removeAddToChatButton();
          }
        });

        // Remove the button when the selection changes and becomes empty
        editor.onDidChangeCursorSelection(() => {
          const selection = editor.getSelection();
          if (selection?.isEmpty()) {
            removeAddToChatButton();
          }
        });

        editorDomNodeRef.current = editor.getDomNode() as HTMLElement;

        document.addEventListener("click", handleGlobalClick);
        editor.onDidDispose(() => {
          document.removeEventListener("click", handleGlobalClick);
        });
      }}
    />
  );
}
