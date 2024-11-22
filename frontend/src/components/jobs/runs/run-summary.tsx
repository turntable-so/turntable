import type { Run } from "@/app/actions/actions";
import { Card, CardContent } from "@/components/ui/card";
import Convert from "ansi-to-html";

type RunSummaryProps = {
  run: Run;
};

export default function RunSummary({ run }: RunSummaryProps) {
  const convert = new Convert();

  const isError = run.status === "FAILURE";

  const ErrorContent = ({ traceback }: { traceback: string }) => {
    const html = convert.toHtml(traceback);
    return (
      <p
        className="whitespace-pre-wrap break-words text-red-500"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  };

  const SuccessContent = ({
    stdouts,
    task_kwargs,
  }: {
    stdouts: Array<string>;
    task_kwargs: any;
  }) => {
    console.log({ stdouts, task_kwargs });
    return <p>{stdouts.join("\n")}</p>;
  };

  return (
    <Card>
      <CardContent className="p-6 text-sm">
        {isError ? (
          <ErrorContent traceback={run.traceback} />
        ) : (
          <SuccessContent
            stdouts={run.result.stdouts}
            task_kwargs={run.task_kwargs}
          />
        )}
      </CardContent>
    </Card>
  );
}
