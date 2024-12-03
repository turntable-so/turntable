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
          h1: "h2",
          h2: "h3",
          h3: "h4",
          h4: "h5",
          h5: "h6",
          h6: "p",
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
