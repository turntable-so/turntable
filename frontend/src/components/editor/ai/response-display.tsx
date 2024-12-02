import { useTheme } from "next-themes";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  darcula as darkStyle,
  prism as lightStyle,
} from "react-syntax-highlighter/dist/cjs/styles/prism";

interface ResponseDisplayProps {
  content: string;
}

export default function ResponseDisplay({ content }: ResponseDisplayProps) {
  const { resolvedTheme } = useTheme();
  const syntaxStyle = resolvedTheme === "dark" ? darkStyle : lightStyle;

  return (
    <div className="overflow-y-auto prose max-w-none dark:prose-invert">
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
