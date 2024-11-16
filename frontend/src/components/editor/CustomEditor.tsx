import { useRef, useEffect } from "react";
import { Editor } from "@monaco-editor/react";
import { useTheme } from "next-themes";

interface CustomEditorProps {
  value?: string;
  language?: string;
  options?: any;
  height?: number | string;
  width?: number | string;
  [key: string]: any;
}

export default function CustomEditor(props: CustomEditorProps) {
  const { resolvedTheme } = useTheme();
  const monacoRef = useRef<any>(null);

  const customTheme = {
    base: resolvedTheme === "dark" ? "vs-dark" : "vs",
    inherit: true,
    rules: [],
    colors: {
      "editor.foreground": resolvedTheme === "dark" ? "#ffffff" : "#000000",
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
    <Editor
      {...props}
      beforeMount={(monaco) => {
        monacoRef.current = monaco;
        monaco.editor.defineTheme("mutedTheme", customTheme);
      }}
      onMount={(editor) => {
        editor.updateOptions({ theme: "mutedTheme" });
      }}
      theme="mutedTheme"
    />
  );
}
