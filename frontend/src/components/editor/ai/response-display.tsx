import { type OpenedFile, useFiles } from "@/app/contexts/FilesContext";
import { useThrottleState } from "@/app/hooks/use-throttle-state";
import { useWebSocket } from "@/app/hooks/use-websocket";
import getUrl from "@/app/url";
import { Button } from "@/components/ui/button";
import { AuthActions } from "@/lib/auth";
import { Copy } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  darcula as darkStyle,
  prism as lightStyle,
} from "react-syntax-highlighter/dist/cjs/styles/prism";
import { useCopyToClipboard } from "usehooks-ts";
import type { InstantApplyPayload } from "./types";

const baseUrl = getUrl();
const base = new URL(baseUrl).host;
const protocol = process.env.NODE_ENV === "development" ? "ws" : "wss";

interface ResponseDisplayProps {
  content: string;
}

export default function ResponseDisplay({ content }: ResponseDisplayProps) {
  const { resolvedTheme } = useTheme();
  const { activeFile, setActiveFile, isApplying, setIsApplying } = useFiles();
  const [_, copy] = useCopyToClipboard();
  const syntaxStyle = resolvedTheme === "dark" ? darkStyle : lightStyle;

  const [error, setError] = useState<string | null>(null);
  const { getToken } = AuthActions();
  const accessToken = getToken("access");

  // A local throttled state for partial diff updates
  const [throttledFile, throttledSetFile] = useThrottleState<OpenedFile | null>(
    activeFile,
    1000,
  );

  // We store the appended content in a ref
  const accumulatedContent = useRef<string>("");

  const { startWebSocket, sendMessage, stopWebSocket } =
    useWebSocket<InstantApplyPayload>(
      `${protocol}://${base}/ws/instant_apply/?token=${accessToken}`,
      {
        onOpen: ({ payload }) => {
          sendMessage(JSON.stringify(payload));
          setIsApplying(true);

          // Create a new active file with apply mode
          const newActiveFile = {
            ...activeFile,
            view: "apply",
            diff: {
              original: activeFile?.content ?? "",
              modified: "",
            },
          } as OpenedFile;

          // Update both the active file and throttled file state
          setActiveFile(newActiveFile);
          throttledSetFile(newActiveFile); // Set the initial throttled state
        },
        onMessage: ({ event }) => {
          const data = JSON.parse(event.data);

          if (data.type === "message_chunk") {
            // Accumulate chunk data
            accumulatedContent.current += data.content;

            // Throttle the "apply" update
            throttledSetFile((prev) => {
              return {
                ...prev,
                view: "apply",
                diff: {
                  original: prev?.content ?? "",
                  modified: accumulatedContent.current,
                },
              };
            });
          } else if (data.type === "message_end") {
            setIsApplying(false);
            stopWebSocket();
            accumulatedContent.current = "";
          } else if (data.type === "error") {
            setError(data.message);
            setIsApplying(false);
            stopWebSocket();
            accumulatedContent.current = "";
          }
        },
        onError: ({ event }) => {
          console.error("WebSocket error:", event);
          setIsApplying(false);
          stopWebSocket();
          accumulatedContent.current = "";
        },
      },
    );

  // These effects maintain bidirectional sync between activeFile and throttledFile:
  // 1. When throttledFile changes (from streaming updates), update activeFile
  // 2. When activeFile changes (from user switching files), update throttledFile
  useEffect(() => {
    if (throttledFile) {
      setActiveFile(throttledFile);
    }
  }, [throttledFile]);

  useEffect(() => {
    throttledSetFile(activeFile);
  }, [activeFile]);

  const handleApply = (code: string) => {
    if (!activeFile || isApplying || typeof activeFile.content !== "string")
      return;
    startWebSocket({
      base_file: activeFile.content,
      change: code,
    });
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
                <div className="flex gap-2 p-1">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => copy(codeString)}
                  >
                    <Copy className="w-4 h-4 mr-2" />
                    Copy
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={isApplying}
                    onClick={() => handleApply(codeString)}
                  >
                    {isApplying ? "Applying" : "Apply"}
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
