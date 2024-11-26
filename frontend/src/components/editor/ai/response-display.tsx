import Markdown from "react-markdown";
import { AICodeBlock } from "./ai-code-block";

interface ResponseDisplayProps {
  response: string;
}

export default function ResponseDisplay({ response }: ResponseDisplayProps) {
  return (
    <div className="overflow-x-hidden space-y-4 mt-4">
      <Markdown
        children={response}
        className="prose dark:prose-invert max-w-none [&_pre]:!p-0 [&_pre]:!m-0 [&_pre]:!border-none [&_code]:!border-none"
        components={{
          code: AICodeBlock,
        }}
      />
    </div>
  );
}