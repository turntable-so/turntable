"use client";

import type { Job, Run } from "@/app/actions/actions";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import RunArtifacts from "./run-artifacts";
import RunDetails from "./run-details";
import RunSummary from "./run-summary";

type JobRunIdPageProps = {
  run: Run;
  job: Job;
};

export default function JobRunIdPage({ run, job }: JobRunIdPageProps) {
  const TabNames = {
    summary: "Summary",
    artifacts: "Artifacts",
  };

  return (
    <div className="flex flex-col gap-4">
      <RunDetails run={run} />
      <Tabs defaultValue={TabNames.summary}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value={TabNames.summary}>{TabNames.summary}</TabsTrigger>
          <TabsTrigger value={TabNames.artifacts}>
            {TabNames.artifacts}
          </TabsTrigger>
        </TabsList>
        <TabsContent value={TabNames.summary}>
          <RunSummary run={run} />
        </TabsContent>
        <TabsContent value={TabNames.artifacts}>
          <RunArtifacts run={run} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
