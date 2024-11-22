import type { Job } from "@/app/actions/actions";
import { Card, CardHeader, CardTitle, CardDescription } from "../ui/card";
import cronstrue from "cronstrue";
import Link from "next/link";
import dayjs from "@/lib/dayjs";
import StatusIcon from "./status-icon";

type JobCardProps = {
  job: Job;
};

export default function JobCard({ job }: JobCardProps) {
  const cronExpression = job.cron_str
    ? cronstrue.toString(job.cron_str)
    : "No cron expression";

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
            <StatusIcon
              status={job.latest_run?.status || "STARTED"}
              size="lg"
            />
            <div className="w-full">
              <div className="flex justify-between items-center">
                <div className="flex flex-col gap-1">
                  <CardTitle>{job.name}</CardTitle>
                  <CardDescription>{cronExpression}</CardDescription>
                </div>

                <div className="text-sm text-muted-foreground">
                  <div className="flex items-center justify-end gap-2">
                    {lastRunDate ? (
                      <p>
                        Last run {hasSucceeded ? "succeeded" : "failed"}{" "}
                        {formattedLastRunDate}
                      </p>
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
