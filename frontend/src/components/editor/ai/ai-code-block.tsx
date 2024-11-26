import { Copy, RedoDot } from "lucide-react";
import type React from "react";
import { useRef } from "react";
import { Button } from "../../ui/button";
import CustomEditor from "../CustomEditor";

interface CodeProps {
  children: React.ReactNode;
  className?: string;
}

export const AICodeBlock: React.FC<CodeProps> = ({ children, className, ...rest }) => {
  const match = /language-(\w+)/.exec(className || "");
  const lineCount = String(children).split("\n").length;
  const height = `${lineCount * 22}px`;
  const editorRef = useRef<any>(null);

  if (match) {
    return (
      <div style={{ height, overflow: "hidden", border: "none" }}>
        <div className="flex justify-end">
          <Button
            size="sm"
            variant="ghost"
            className="items-center flex space-x-2"
            onClick={() => {
              navigator.clipboard.writeText(String(children));
            }}
          >
            <Copy className="w-3 h-3" />
            <div>Copy</div>
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="items-center flex space-x-2"
          >
            <RedoDot className="w-3 h-3" />
            <div>Apply</div>
          </Button>
        </div>
        <CustomEditor
          className="pointer-events-none select-none"
          key={"fixed"}
          value={String(children).replace(/\n$/, "")}
          language={match[1]}
          options={{
            minimap: { enabled: false },
            scrollbar: {
              vertical: "hidden",
              horizontal: "hidden",
              verticalScrollbarSize: 0,
              horizontalScrollbarSize: 0,
            },
            lineNumbers: "off",
            wordWrap: "on",
            fontSize: 14,
            lineNumbersMinChars: 3,
            renderLineHighlight: "none",
            readOnly: true,
            overviewRulerBorder: false,
            hideCursorInOverviewRuler: true,
            overviewRulerLanes: 0,
          }}
          height={height}
          onMount={(editor, monaco) => {
            editorRef.current = editor;
            const model = editor.getModel();
            if (model) {
              model.setValue(String(children).replace(/\n$/, ""));
            }
          }}
          onChange={(value, event) => {
            if (editorRef.current) {
              const model = editorRef.current.getModel();
              if (model) {
                model.applyEdits([
                  {
                    range: model.getFullModelRange(),
                    text: value,
                  },
                ]);
              }
            }
          }}
        />
      </div>
    );
  }

  return <code {...rest} className={className}>{children}</code>;
};