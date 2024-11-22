import type { RunWithJob } from "@/app/actions/actions";
import dayjs from "@/lib/dayjs";
import { truncateUuid } from "@/lib/id-utils";
import { capitalize } from "lodash";
import Link from "next/link";
import { Card, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import StatusIcon from "../status-icon";
import { StatusToVerbMap } from "../utils";

type RunCardProps = {
  run: RunWithJob;
};

export default function RunCard({ run }: RunCardProps) {
  const dateDone = run.date_done ? dayjs.utc(run.date_done).fromNow() : null;
  const duration = run.date_done
    ? `${dayjs(run.date_done).diff(run.date_created, "seconds")}s`
    : null;

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
                  <div className="flex items-center justify-end gap-2">
                    <p>Took {duration}</p>
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
