import { useRef, useEffect } from "react";
import { DiffEditor } from "@monaco-editor/react";
import { useTheme } from "next-themes";

interface CustomDiffEditorProps {
  original?: string;
  modified?: string;
  language?: string;
  options?: any;
  height?: number | string;
  width?: number | string;
  [key: string]: any;
}

export default function CustomDiffEditor(props: CustomDiffEditorProps) {
  const { resolvedTheme } = useTheme();
  const monacoRef = useRef<any>(null);

  const customTheme = {
    base: resolvedTheme === "dark" ? "vs-dark" : "vs",
    inherit: true,
    rules: [],
    colors: {
      "editor.foreground": "#000000",
      "editorLineNumber.foreground": "#A1A1AA",
    },
  };

  useEffect(() => {
    if (monacoRef.current) {
      monacoRef.current.editor.defineTheme("mutedTheme", customTheme);
      monacoRef.current.editor.setTheme("mutedTheme");
    }
  }, [resolvedTheme]);

  return (
    <DiffEditor
      {...props}
      beforeMount={(monaco: any) => {
        monacoRef.current = monaco;
        monaco.editor.defineTheme("mutedTheme", customTheme);
      }}
      onMount={(editor: any) => {
        editor.updateOptions({ theme: "mutedTheme" });
      }}
      theme="mutedTheme"
    />
  );
}
