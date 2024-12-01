import type { Run } from "@/app/actions/actions";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import Convert from "ansi-to-html";
import { ChevronsUpDown, Loader2 } from "lucide-react";

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
    const subtasks = run.subtasks || [];

    return (
      <div>
        {subtasks.length > 0 ? (
          subtasks.map((subtask, index) => (
            <Collapsible
              key={subtask?.task_id || index}
              className="w-full space-y-2 mb-4"
              defaultOpen
            >
              <div className="flex items-center justify-between space-x-4 px-4">
                <h4 className="text-sm font-semibold">{subtask?.task_kwargs?.command}</h4>
                <CollapsibleTrigger asChild>
                  <Button variant="ghost" size="sm" className="w-9 p-0">
                    <ChevronsUpDown className="h-4 w-4" />
                    <span className="sr-only">Toggle</span>
                  </Button>
                </CollapsibleTrigger>
              </div>
              <CollapsibleContent>
                <div className="rounded-md border px-4 py-3 font-mono text-sm whitespace-pre-wrap break-words">
                  {subtask?.result?.stdout ? (
                    <p dangerouslySetInnerHTML={{ __html: convert.toHtml(subtask.result.stdout) }} />
                  ) : (
                    <Loader2 className="animate-spin" />
                  )}
                </div>
              </CollapsibleContent>
            </Collapsible>
          ))
        ) : (
          <div className="flex justify-center">
            <Loader2 className="animate-spin" />
          </div>
        )}
      </div>
    );
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
