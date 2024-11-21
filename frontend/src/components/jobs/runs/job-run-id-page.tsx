"use client";

import type { Job, Run } from "@/app/actions/actions";
import FullWidthPageLayout from "@/components/layout/FullWidthPageLayout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Play } from "lucide-react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";

dayjs.extend(relativeTime);

type JobRunIdPageProps = {
  run: Run;
  job: Job;
};

export default function JobRunIdPage({ run, job }: JobRunIdPageProps) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "success":
        return "bg-green-500/10 text-green-500";
      case "error":
        return "bg-red-500/10 text-red-500";
      case "running":
        return "bg-blue-500/10 text-blue-500";
      default:
        return "bg-gray-500/10 text-gray-500";
    }
  };

  const RunAgainButton = () => {
    return (
      <Button
        className="rounded-full"
        onClick={() => {
          console.log("Run again");
        }}
      >
        <Play className="w-4 h-4 mr-2" />
        Run Again
      </Button>
    );
  };

  return (
    <FullWidthPageLayout
      title={`${job.name} / Run ${run.task_id}`}
      button={<RunAgainButton />}
    >
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Badge
              variant="secondary"
              className={`${getStatusColor(run.status)}`}
            >
              {run.status}
            </Badge>
            <p className="text-sm text-muted-foreground">
              {dayjs(run.date_created).fromNow()}
            </p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Run Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
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
                  {run.date_done
                    ? `${dayjs(run.date_done).diff(run.date_created, "seconds")}s`
                    : "Running..."}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Triggered By
                </p>
                <p className="text-sm">{"Manual"}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Environment
                </p>
                <p className="text-sm">{"Production"}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </FullWidthPageLayout>
  );
}
