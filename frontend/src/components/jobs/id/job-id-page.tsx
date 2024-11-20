"use client";

import FullWidthPageLayout from "@/components/layout/FullWidthPageLayout";
import type { Job } from "@/app/actions/actions";
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

type JobIdPageProps = {
  job: Job;
};

export default function JobIdPage({ job }: JobIdPageProps) {
  const RunNowButton = () => {
    return (
      <Button
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
    <FullWidthPageLayout title={job.id} button={<RunNowButton />}>
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <p className="text-sm font-medium">Next Run</p>
          <p className="flex items-center gap-2 text-sm text-muted-foreground">
            <AlarmClock className="w-4 h-4" />
            {job.cron_str}
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Recent runs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-4 gap-4">
              <div className="flex flex-col">
                <p className="text-sm font-medium text-muted-foreground">
                  Success rate
                </p>
                <p className="text-xl font-bold">100%</p>
              </div>
              <div className="flex flex-col">
                <p className="text-sm font-medium text-muted-foreground">
                  Completed
                </p>
                <p className="text-xl font-bold">12</p>
              </div>
              <div className="flex flex-col">
                <p className="text-sm font-medium text-muted-foreground">
                  Succeeded
                </p>
                <p className="text-xl font-bold">12</p>
              </div>
              <div className="flex flex-col">
                <p className="text-sm font-medium text-muted-foreground">
                  Errored
                </p>
                <p className="text-xl font-bold">3</p>
              </div>
            </div>
            <div className="flex items-center justify-center py-8">
              <div className="flex flex-col items-center text-muted-foreground">
                <CircleHelp className="w-6 h-6" />
                <p>No recent runs</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Run history</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4">
              <Select defaultValue="all">
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="succeeded">Succeeded</SelectItem>
                  <SelectItem value="errored">Errored</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center justify-center py-8">
              <div className="flex flex-col items-center text-muted-foreground">
                <CircleHelp className="w-6 h-6" />
                <p>No runs found</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </FullWidthPageLayout>
  );
}
