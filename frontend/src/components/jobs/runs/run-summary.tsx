import type { Run } from "@/app/actions/actions";
import { Card, CardContent } from "@/components/ui/card";
import Convert from "ansi-to-html";
import { Loader2 } from "lucide-react";
import React, { useRef } from "react";

const LogOutput = React.memo(function LogOutput({
  content,
  isError = false,
}: {
  content: string;
  isError?: boolean;
}) {
  const convert = new Convert();
  const scrollRef = useRef<HTMLDivElement>(null);

  return (
    <div
      ref={scrollRef}
      className={`rounded-md border px-4 py-3 font-mono text-sm whitespace-pre-wrap break-words ${
        isError ? "text-red-500" : ""
      }`}
      style={{ maxHeight: "400px", overflow: "auto" }}
    >
      <p
        dangerouslySetInnerHTML={{
          __html: convert.toHtml(content),
        }}
      />
    </div>
  );
});

const SubtaskContent = React.memo(function SubtaskContent({
  subtask,
}: {
  subtask: Run["subtasks"][number];
}) {
  const { status, result, subtasks, task_kwargs, traceback } = subtask;
  const command = task_kwargs?.command || task_kwargs?.commands?.join(" ");
  const hasSubtasks = subtasks && subtasks.length > 0;

  return (
    <Card>
      <CardContent>
        <div className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold">{command}</h4>
          </div>
          {status === "SUCCESS" && result?.stdout ? (
            <LogOutput content={result.stdout} />
          ) : status === "FAILURE" && traceback ? (
            <LogOutput content={traceback} isError />
          ) : status === "STARTED" && result?.stdout ? (
            <div className="space-y-2">
              <LogOutput content={result.stdout} />
              <div className="flex justify-center">
                <Loader2 className="animate-spin" />
              </div>
            </div>
          ) : (
            <Loader2 className="animate-spin" />
          )}
          {hasSubtasks &&
            subtasks.map((childSubtask) => (
              <div key={childSubtask.task_id} className="pl-4 border-l mt-4">
                <SubtaskContent subtask={childSubtask} />
              </div>
            ))}
        </div>
      </CardContent>
    </Card>
  );
});

export default function RunSummary({ run }: { run: Run }) {
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
