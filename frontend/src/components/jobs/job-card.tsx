import type { Job } from "@/app/actions/actions";
import { getResourceIcon } from "@/lib/utils";
import { Card, CardHeader, CardTitle, CardDescription } from "../ui/card";
import cronstrue from "cronstrue";
import { CheckCircle2, CircleX } from "lucide-react";
import Link from "next/link";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import { Fragment } from "react";

dayjs.extend(relativeTime);

type JobCardProps = {
  job: Job;
};

export default function JobCard({ job }: JobCardProps) {
  const cronExpression = cronstrue.toString(job.cron_str);

  const hasSucceeded = job.latest_run?.status === "SUCCESS";
  const lastRunDate = job.latest_run?.date_done;
  const formattedLastRunDate = lastRunDate
    ? dayjs(lastRunDate).fromNow()
    : null;
  const nextRunDate = job.next_run ? dayjs(job.next_run).fromNow() : null;

  return (
    <Link href={`/jobs/${job.id}`}>
      <Card className="rounded-md hover:border-black hover:dark:border-white">
        <CardHeader>
          <div className="flex items-center space-x-4">
            <div className="mb-1 space-y-1">{getResourceIcon("dbt")}</div>
            <div className="w-full">
              <div className="flex justify-between items-center">
                <div className="flex flex-col gap-1">
                  <CardTitle>{job.name}</CardTitle>
                  <CardDescription>{cronExpression}</CardDescription>
                </div>

                <div className="text-sm text-muted-foreground">
                  <div className="flex items-center justify-end gap-2">
                    {lastRunDate ? (
                      <Fragment>
                        <p>
                          Last run {hasSucceeded ? "succeeded" : "failed"}{" "}
                          {formattedLastRunDate}
                        </p>
                        {hasSucceeded ? (
                          <CheckCircle2 className={"w-4 h-4 text-green-500"} />
                        ) : (
                          <CircleX className={"w-4 h-4 text-red-500"} />
                        )}
                      </Fragment>
                    ) : (
                      <p>Not ran yet</p>
                    )}
                  </div>
                  <div className="flex items-center justify-end gap-2">
                    {nextRunDate ? `Next run ${nextRunDate}` : "No next run"}
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
