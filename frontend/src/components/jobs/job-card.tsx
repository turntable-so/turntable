import type { Job } from "@/app/actions/actions";
import { getResourceIcon } from "@/lib/utils";
import { Card, CardHeader, CardTitle, CardDescription } from "../ui/card";
import cronstrue from "cronstrue";
import { CheckCircle2 } from "lucide-react";
import Link from "next/link";

type JobCardProps = {
  job: Job;
};

export default function JobCard({ job }: JobCardProps) {
  const cronExpression = cronstrue.toString(job.cron_str);

  return (
    <Link href={`/jobs/${job.id}`}>
      <Card className="rounded-md hover:border-black hover:dark:border-white">
        <CardHeader>
          <div className="flex items-center space-x-4">
            <div className="mb-1 space-y-1">{getResourceIcon("dbt")}</div>
            <div className="w-full">
              <div className="flex justify-between items-center">
                <div className="space-y-1">
                  <CardTitle>(H) Production run</CardTitle>
                  <CardDescription>
                    <div>
                      <p>(H) Schedule</p>
                      {cronExpression}
                    </div>
                  </CardDescription>
                </div>

                <div className="text-sm text-muted-foreground">
                  <div className="flex items-center justify-end gap-2">
                    {"(H) Last run succeeded 47m ago"}
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                  </div>
                  <div className="flex items-center justify-end gap-2">
                    {"(H) Next run in 1 hour"}
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
