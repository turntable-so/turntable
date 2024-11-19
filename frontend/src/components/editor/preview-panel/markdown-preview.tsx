import React from "react";
import { useTheme } from "next-themes";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { darcula as darkStyle } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { prism as lightStyle } from "react-syntax-highlighter/dist/cjs/styles/prism";

type MarkdownPreviewProps = {
  content: string;
};

export default function MarkdownPreview({ content }: MarkdownPreviewProps) {
  const { resolvedTheme } = useTheme();
  const syntaxStyle = resolvedTheme === "dark" ? darkStyle : lightStyle;

  return (
    <div className="markdown-preview p-4 overflow-y-auto prose max-w-none dark:prose-invert">
      <ReactMarkdown
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            return !inline && match ? (
              <SyntaxHighlighter
                style={syntaxStyle}
                language={match[1]}
                PreTag="div"
                {...props}
              >
                {String(children).replace(/\n$/, "")}
              </SyntaxHighlighter>
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
