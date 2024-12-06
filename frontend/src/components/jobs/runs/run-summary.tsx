import type { Run } from "@/app/actions/actions";
import { Card, CardContent } from "@/components/ui/card";
import Convert from "ansi-to-html";
import { Loader2 } from "lucide-react";

export default function RunSummary({ run }: { run: Run }) {
  const convert = new Convert();

  function SubtaskContent({
    subtask,
  }: {
    subtask: Run["subtasks"][number];
  }) {
    const status = subtask.status;
    const command =
      subtask.task_kwargs?.command || subtask.task_kwargs?.commands?.join(" ");
    const hasSubtasks = subtask.subtasks && subtask.subtasks.length > 0;

    return (
      <Card>
        <CardContent>
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold">{command}</h4>
            </div>
            {status === "SUCCESS" && subtask.result?.stdout ? (
              <div
                className="rounded-md border px-4 py-3 font-mono text-sm whitespace-pre-wrap break-words"
                style={{ maxHeight: "400px", overflow: "auto" }}
              >
                <p
                  dangerouslySetInnerHTML={{
                    __html: convert.toHtml(subtask.result.stdout),
                  }}
                />
              </div>
            ) : status === "FAILURE" && subtask.traceback ? (
              <div
                className="rounded-md border px-4 py-3 font-mono text-sm whitespace-pre-wrap break-words text-red-500"
                style={{ maxHeight: "400px", overflow: "auto" }}
              >
                <p
                  dangerouslySetInnerHTML={{
                    __html: convert.toHtml(subtask.traceback),
                  }}
                />
              </div>
            ) : (
              <Loader2 className="animate-spin" />
            )}
            {hasSubtasks &&
              subtask.subtasks.map((childSubtask) => (
                <div key={childSubtask.task_id} className="pl-4 border-l mt-4">
                  <SubtaskContent subtask={childSubtask} />
                </div>
              ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="flex flex-col gap-4 overflow-auto">
      {run.subtasks && run.subtasks.length > 0 ? (
        run.subtasks.map((subtask) => (
          <SubtaskContent key={subtask.task_id} subtask={subtask} />
        ))
      ) : (
        <div className="flex justify-center">
          <Loader2 className="animate-spin" />
        </div>
      )}
    </div>
  );
}
