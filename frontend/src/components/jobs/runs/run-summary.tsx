import type { Run } from "@/app/actions/actions";
import { Card, CardContent } from "@/components/ui/card";
import Convert from "ansi-to-html";
import * as React from "react";
import { ChevronsUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

type RunSummaryProps = {
  run: Run;
};

export default function RunSummary({ run }: RunSummaryProps) {
  const convert = new Convert();

  const ErrorContent = ({ traceback }: { traceback: string }) => {
    const html = convert.toHtml(traceback);
    return (
      <p
        className="whitespace-pre-wrap break-words text-red-500"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  };

  const SuccessContent = () => {
    const stdouts = run.result.stdouts || [];
    const commands = run.task_kwargs?.commands || [];

    return (
      <div>
        {commands.map((command, index) => (
          <Collapsible
            key={index}
            className="w-full space-y-2 mb-4"
            defaultOpen
          >
            <div className="flex items-center justify-between space-x-4 px-4">
              <h4 className="text-sm font-semibold">{command}</h4>
              <CollapsibleTrigger asChild>
                <Button variant="ghost" size="sm" className="w-9 p-0">
                  <ChevronsUpDown className="h-4 w-4" />
                  <span className="sr-only">Toggle</span>
                </Button>
              </CollapsibleTrigger>
            </div>
            <CollapsibleContent>
              <div className="rounded-md border px-4 py-3 font-mono text-sm whitespace-pre-wrap break-words">
                {stdouts[index]}
              </div>
            </CollapsibleContent>
          </Collapsible>
        ))}
      </div>
    );
  };

  const StartedContent = () => {
    return <p>Started</p>;
  };

  const StatusComponentMap = {
    SUCCESS: () => <SuccessContent />,
    FAILURE: () => <ErrorContent traceback={run.traceback} />,
    STARTED: () => <SuccessContent />,
  };

  return (
    <Card>
      <CardContent className="p-6 text-sm">
        {StatusComponentMap[run.status]()}
      </CardContent>
    </Card>
  );
}
