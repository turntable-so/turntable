import { useFiles } from "@/app/contexts/FilesContext";
import { Button } from "@/components/ui/button";
import { useTheme } from "next-themes";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { Copy } from "lucide-react";
import {
  darcula as darkStyle,
  prism as lightStyle,
} from "react-syntax-highlighter/dist/cjs/styles/prism";

interface ResponseDisplayProps {
  content: string;
}

export default function ResponseDisplay({ content }: ResponseDisplayProps) {
  const { resolvedTheme } = useTheme();
  const { updateFileContent, activeFile } = useFiles();
  const syntaxStyle = resolvedTheme === "dark" ? darkStyle : lightStyle;

  const handleApply = (code: string) => {
    if (activeFile) {
      updateFileContent(activeFile.node.path, code);
    }
  };

  return (
    <div className="overflow-y-auto prose max-w-none dark:prose-invert">
      <ReactMarkdown
        components={{
          h1: "h3",
          h2: "h4",
          h3: "h5",
          h4: "h6",
          h5: ({ children }) => <p className="text-sm">{children}</p>,
          h6: ({ children }) => <p className="text-sm">{children}</p>,
          p: ({ children }) => <p className="text-sm">{children}</p>,
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            const codeString = String(children).replace(/\n$/, "");
            return !inline && match ? (
              <div className="relative">
                <SyntaxHighlighter
                  style={syntaxStyle}
                  language={match[1]}
                  PreTag="div"
                  {...props}
                >
                  {codeString}
                </SyntaxHighlighter>
                <div className="absolute top-1 right-1 flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      navigator.clipboard.writeText(codeString);
                    }}
                  >
                    <Copy className="w-4 h-4 mr-2" />
                    Copy
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleApply(codeString)}
                  >
                    Apply
                  </Button>
                </div>
              </div>
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
