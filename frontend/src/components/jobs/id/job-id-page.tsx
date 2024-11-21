"use client";

import FullWidthPageLayout from "@/components/layout/FullWidthPageLayout";
import type {
  Job,
  JobAnalytics,
  PaginatedResponse,
  Run,
} from "@/app/actions/actions";
import { Button } from "@/components/ui/button";
import { AlarmClock, CircleHelp, Play } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import dayjs from "dayjs";
import RunsList from "../runs/runs-list";

type JobIdPageProps = {
  job: Job;
  paginatedRuns: PaginatedResponse<Run>;
  page: number;
  pageSize: number;
  jobAnalytics: JobAnalytics;
};

export default function JobIdPage({
  job,
  paginatedRuns,
  page,
  pageSize,
  jobAnalytics,
}: JobIdPageProps) {
  const runsWithJob = paginatedRuns.results.map((run) => ({
    ...run,
    job_name: job.name,
    job_id: job.id,
  }));

  const RunNowButton = () => {
    return (
      <Button
        className="rounded-full"
        onClick={() => {
          console.log("Run job");
        }}
      >
        <Play className="w-4 h-4 mr-2" />
        Run Now
      </Button>
    );
  };

  return (
    <FullWidthPageLayout title={job.name} button={<RunNowButton />}>
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <p className="text-sm font-medium">Next Run</p>
          <p className="flex items-center gap-2 text-muted-foreground">
            <AlarmClock className="w-4 h-4" />
            {job.next_run
              ? dayjs(job.next_run).format("MMM D, YYYY, h:mma")
              : "No next run"}
          </p>
        </div>

        <Card>
          <CardContent className="p-6">
            <p className="text-xs text-muted-foreground mb-4">Last 100 runs</p>
            <div className="grid grid-cols-4 gap-4">
              <div className="flex flex-col">
                <p className="text-sm font-medium text-muted-foreground">
                  Success rate
                </p>
                <p className="text-xl font-bold">
                  {jobAnalytics.success_rate}%
                </p>
              </div>
              <div className="flex flex-col">
                <p className="text-sm font-medium text-muted-foreground">
                  Completed
                </p>
                <p className="text-xl font-bold">{jobAnalytics.completed}</p>
              </div>
              <div className="flex flex-col">
                <p className="text-sm font-medium text-muted-foreground">
                  Succeeded
                </p>
                <p className="text-xl font-bold">{jobAnalytics.succeeded}</p>
              </div>
              <div className="flex flex-col">
                <p className="text-sm font-medium text-muted-foreground">
                  Errored
                </p>
                <p className="text-xl font-bold">{jobAnalytics.errored}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Run history</CardTitle>
              {/* <Select defaultValue="all">
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="succeeded">Succeeded</SelectItem>
                  <SelectItem value="errored">Errored</SelectItem>
                </SelectContent>
              </Select> */}
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center">
              {runsWithJob.length > 0 ? (
                <RunsList
                  runs={runsWithJob}
                  page={page}
                  pageSize={pageSize}
                  count={paginatedRuns.count}
                />
              ) : (
                <div className="flex flex-col items-center text-muted-foreground">
                  <CircleHelp className="w-6 h-6" />
                  <p>No runs</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </FullWidthPageLayout>
  );
}
