import type { RunWithJob } from "@/app/actions/actions";
import dayjs from "@/lib/dayjs";
import { truncateUuid } from "@/lib/id-utils";
import { capitalize } from "lodash";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Card, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import StatusIcon from "../status-icon";
import { StatusToVerbMap } from "../utils";

type RunCardProps = {
  run: RunWithJob;
};

export default function RunCard({ run }: RunCardProps) {
  const dateDone = run.date_done ? dayjs.utc(run.date_done).fromNow() : null;

  const duration = run.date_done
    ? dayjs(run.date_done).diff(run.date_created, "seconds")
    : null;

  const [elapsedTime, setElapsedTime] = useState<number | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (run.status === "STARTED") {
      const updateElapsedTime = () => {
        const now = dayjs();
        const created = dayjs(run.date_created);
        const secondsElapsed = now.diff(created, "seconds");
        setElapsedTime(secondsElapsed);
      };

      updateElapsedTime();
      interval = setInterval(updateElapsedTime, 1000);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [run.status, run.date_created]);

  return (
    <Link href={`/jobs/${run.job_id}/run/${run.task_id}`}>
      <Card className="rounded-md hover:border-black hover:dark:border-white">
        <CardHeader>
          <div className="flex items-center space-x-4">
            <div className="mb-1 space-y-1">
              <StatusIcon status={run.status} size="lg" />
            </div>
            <div className="w-full">
              <div className="flex justify-between items-center">
                <div className="flex flex-col gap-1">
                  <CardTitle>Run {truncateUuid(run.task_id)}</CardTitle>
                  <CardDescription>{run.job_name}</CardDescription>
                </div>

                <div className="text-sm text-muted-foreground">
                  <div className="flex items-center justify-end gap-2">
                    {dateDone ? (
                      <p>
                        {capitalize(StatusToVerbMap[run.status || "UNKNOWN"])}{" "}
                        {dateDone}
                      </p>
                    ) : (
                      <p>Not completed yet</p>
                    )}
                  </div>
                  {run.status === "STARTED" && elapsedTime !== null ? (
                    <div className="flex items-center justify-end gap-2">
                      <p>{elapsedTime}s elapsed</p>
                    </div>
                  ) : duration && duration !== 0 ? (
                    <div className="flex items-center justify-end gap-2">
                      <p>Took {duration}s</p>
                    </div>
                  ) : null}
                </div>
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>
    </Link>
  );
}
