import type { RunWithJob } from "@/app/actions/actions";
import { Card, CardHeader, CardTitle, CardDescription } from "../../ui/card";
import { CheckCircle2, CircleX } from "lucide-react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import Link from "next/link";

dayjs.extend(relativeTime);

type RunCardProps = {
  run: RunWithJob;
};

export default function RunCard({ run }: RunCardProps) {
  const hasSucceeded = run.status === "SUCCESS";
  const dateDone = run.date_done ? dayjs(run.date_done).fromNow() : null;

  return (
    <Link href={`/jobs/${run.job_id}/run/${run.task_id}`}>
      <Card className="rounded-md hover:border-black hover:dark:border-white">
        <CardHeader>
          <div className="flex items-center space-x-4">
            <div className="mb-1 space-y-1">
              {hasSucceeded ? (
                <CheckCircle2 className="w-6 h-6 text-green-500" />
              ) : (
                <CircleX className="w-6 h-6 text-red-500" />
              )}
            </div>
            <div className="w-full">
              <div className="flex justify-between items-center">
                <div className="flex flex-col gap-1">
                  <CardTitle>Run {run.task_id}</CardTitle>
                  <CardDescription>{run.job_name}</CardDescription>
                </div>

                <div className="text-sm text-muted-foreground">
                  <div className="flex items-center justify-end gap-2">
                    {dateDone ? (
                      <p>
                        {hasSucceeded ? "Succeeded" : "Failed"} {dateDone}
                      </p>
                    ) : (
                      <p>Not completed yet</p>
                    )}
                  </div>
                  <div className="flex items-center justify-end gap-2">
                    <p>(H) Took 25s</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>
    </Link>
  );
}
