import type { Job } from "@/app/actions/actions";
import dayjs from "@/lib/dayjs";
import cronstrue from "cronstrue";
import Link from "next/link";
import { Card, CardDescription, CardHeader, CardTitle } from "../ui/card";
import StatusIcon from "./status-icon";
import { StatusToVerbMap } from "./utils";

type JobCardProps = {
  job: Job;
};

export default function JobCard({ job }: JobCardProps) {


  const lastRunDate = job.latest_run?.date_done;
  const formattedLastRunDate = lastRunDate
    ? dayjs.utc(lastRunDate).fromNow()
    : null;
  const nextRunDate = job.next_run ? dayjs.utc(job.next_run).fromNow() : null;

  return (
    <Link href={`/jobs/${job.id}`}>
      <Card className="rounded-md hover:border-black hover:dark:border-white">
        <CardHeader>
          <div className="flex items-center space-x-4">
            <StatusIcon
              status={
                lastRunDate
                  ? job.latest_run?.status || "NOT_RAN_YET"
                  : "NOT_RAN_YET"
              }
              size="lg"
            />
            <div className="w-full">
              <div className="flex justify-between items-center">
                <div className="flex flex-col gap-1">
                  <CardTitle>{job.name}</CardTitle>
                  {job.workflow_type === "cron" && (
                    <CardDescription>{cronstrue.toString(job.cron_str); }</CardDescription>
                  )}
                  {job.workflow_type === "webhook" && (
                    <CardDescription>
                      Webhook
                    </CardDescription>
                  )}
                </div>

                <div className="text-sm text-muted-foreground">
                  <div className="flex items-center justify-end gap-2">
                    {lastRunDate ? (
                      <p>
                        Last run{" "}
                        {StatusToVerbMap[job.latest_run?.status || "UNKNOWN"]}{" "}
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
