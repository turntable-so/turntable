import type { Job, Run } from "@/app/actions/actions";
import StatusIcon from "@/components/jobs/status-icon";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import dayjs from "dayjs";
import { capitalize } from "lodash";
import Link from "next/link";

type RunDetailsProps = {
  run: Run;
  job: Job;
};

export default function RunDetails({ run, job }: RunDetailsProps) {
  const trigger = job.cron_str ? "Schedule" : "Manual";

  return (
    <Card>
      <CardHeader>
        <CardTitle>Run Details</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-sm font-medium text-muted-foreground">Status</p>
            <div className="flex items-center gap-2">
              <StatusIcon status={run.status} />
              <p className="text-sm">{capitalize(run.status)}</p>
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Job</p>
            <Link href={`/jobs/${job.id}`} className="w-fit">
              <p className="text-sm underline underline-offset-2 hover:text-primary">
                {job.name}
              </p>
            </Link>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">
              Next Run Date
            </p>
            <p className="text-sm">
              {job.next_run
                ? dayjs(job.next_run).format("MMM D, YYYY h:mm A")
                : "N/A"}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">
              Started At
            </p>
            <p className="text-sm">
              {dayjs(run.date_created).format("MMM D, YYYY h:mm A")}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">
              Duration
            </p>
            <p className="text-sm">
              {run.status !== "STARTED" && run.date_done
                ? `${dayjs(run.date_done).diff(run.date_created, "seconds")}s`
                : "Running..."}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Trigger</p>
            <p className="text-sm">{trigger}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
