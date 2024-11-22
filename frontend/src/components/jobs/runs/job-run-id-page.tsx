"use client";

import type { Job, Run } from "@/app/actions/actions";
import FullWidthPageLayout from "@/components/layout/FullWidthPageLayout";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import RunSummary from "./run-summary";
import RunArtifacts from "./run-artifacts";
import RunDetails from "./run-details";

type JobRunIdPageProps = {
  run: Run;
  job: Job;
};

export default function JobRunIdPage({ run, job }: JobRunIdPageProps) {
  const TabNames = {
    summary: "Summary",
    artifacts: "Artifacts",
  };

  const RunAgainButton = () => {
    return (
      <Button
        className="rounded-full"
        onClick={() => {
          console.log("Run again");
        }}
      >
        <RefreshCw className="w-4 h-4 mr-2" />
        Rerun
      </Button>
    );
  };

  return (
    <FullWidthPageLayout
      title={`${job.name} / Run ${run.task_id}`}
      button={<RunAgainButton />}
    >
      <div className="flex flex-col gap-4">
        <RunDetails run={run} />
        <Tabs defaultValue={TabNames.summary}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value={TabNames.summary}>
              {TabNames.summary}
            </TabsTrigger>
            <TabsTrigger value={TabNames.artifacts}>
              {TabNames.artifacts}
            </TabsTrigger>
          </TabsList>
          <TabsContent value={TabNames.summary}>
            <RunSummary run={run} />
          </TabsContent>
          <TabsContent value={TabNames.artifacts}>
            <RunArtifacts />
          </TabsContent>
        </Tabs>
      </div>
    </FullWidthPageLayout>
  );
}
