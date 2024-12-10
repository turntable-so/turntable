"use client";

import { type OpenedFile, useFiles } from "@/app/contexts/FilesContext";
import { useLayoutContext } from "@/app/contexts/LayoutContext";
import CustomDiffEditor from "@/components/editor/CustomDiffEditor";
import CustomEditor from "@/components/editor/CustomEditor";
import InlineTabSearch from "@/components/editor/search-bar/inline-tab-search";
import { Button } from "@/components/ui/button";
import { Download, Loader2 } from "lucide-react";
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
  } = useFiles();

  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);

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

        editor.addCommand(
            monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyL,
            () => {
              console.log("woo!");
              const selection = editor.getSelection();
              if (selection && !selection.isEmpty()) {
                const selectedText = editor.getModel()?.getValueInRange(selection);
                addToChat(
                  selectedText,
                  selection.startLineNumber,
                  selection.endLineNumber,
                  activeFile?.node.name || ""
                );
              }
            }
          );

        let addToChatButton: HTMLElement | null = null;

        editor.onMouseUp((e) => {
          const selection = editor.getSelection();
          const model = editor.getModel();

          if (selection && !selection.isEmpty()) {
            const position = selection.getStartPosition();

            // Get the pixel position of the start of the selection
            const pixelPosition = editor.getScrolledVisiblePosition(position);

            if (!pixelPosition) {
              return;
            }

            // Get the editor's DOM node and its position on the page
            const editorDomNode = editor.getDomNode() as HTMLElement;
            const editorRect = editorDomNode.getBoundingClientRect();

            // Calculate the absolute position of the pixelPosition relative to the page
            const absoluteLeft =
              editorRect.left + pixelPosition.left - editor.getScrollLeft();
            const absoluteTop =
              editorRect.top + pixelPosition.top - editor.getScrollTop();

            // Remove any existing button
            if (addToChatButton) {
              document.body.removeChild(addToChatButton);
              addToChatButton = null;
            }

            addToChatButton = document.createElement("button");
            addToChatButton.textContent = "Add to Chat (⌘L)";
            addToChatButton.className = "add-to-chat-button";
            addToChatButton.style.position = "absolute";
            addToChatButton.style.left = `${absoluteLeft}px`;
            addToChatButton.style.top = `${absoluteTop}px`;
            addToChatButton.style.transform = "translate(-50%, -100%)";
            addToChatButton.style.zIndex = "1000";

            addToChatButton.onclick = () => {
              const selectedText = model.getValueInRange(selection);
              const startLine = selection.startLineNumber;
              const endLine = selection.endLineNumber;
              const fileName = activeFile?.node.name || "";

              addToChat(selectedText, startLine, endLine, fileName);

              if (addToChatButton) {
                document.body.removeChild(addToChatButton);
                addToChatButton = null;
              }

              editor.setPosition(selection.getEndPosition());
              editor.setSelection(
                new monaco.Selection(
                  selection.endLineNumber,
                  selection.endColumn,
                  selection.endLineNumber,
                  selection.endColumn,
                ),
              );
            };

            // Append the button to the body
            document.body.appendChild(addToChatButton);

            // Ensure the button is within the viewport
            const buttonRect = addToChatButton.getBoundingClientRect();
            const withinViewport =
              buttonRect.top >= 0 &&
              buttonRect.left >= 0 &&
              buttonRect.bottom <= window.innerHeight &&
              buttonRect.right <= window.innerWidth;

            if (!withinViewport) {
              // Center the button if it's outside the viewport
              addToChatButton.style.left = `${window.innerWidth / 2}px`;
              addToChatButton.style.top = `${window.innerHeight / 2}px`;
            }
          } else {
            // Remove the button if selection is empty
            if (addToChatButton) {
              document.body.removeChild(addToChatButton);
              addToChatButton = null;
            }
          }
        });

        // Remove the button when the selection changes and becomes empty
        editor.onDidChangeCursorSelection(() => {
          const selection = editor.getSelection();
          if (selection?.isEmpty() && addToChatButton) {
            document.body.removeChild(addToChatButton);
            addToChatButton = null;
          }
        });

        // Optionally remove the button when the user clicks elsewhere
        editor.onMouseDown(() => {
          if (addToChatButton) {
            document.body.removeChild(addToChatButton);
            addToChatButton = null;
          }
        });
      }}
    />
  );
}
