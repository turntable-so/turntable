import { Plus } from "lucide-react";
import FullWidthPageLayout from "../../components/layout/FullWidthPageLayout";

import { Button } from "@/components/ui/button";
import Link from "next/link";
import { getJobs, getRuns } from "../actions/actions";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import JobsList from "@/components/jobs/jobs-list";
import RunsList from "@/components/jobs/runs-list";

export default async function JobsPage() {
  const runsPromise = getRuns();
  const jobsPromise = getJobs();

  const [runs, jobs] = await Promise.allSettled([runsPromise, jobsPromise]);

  console.log("runs: ", runs);
  console.log("jobs: ", jobs);

  const TabNames = { jobs: "Jobs", runs: "Runs" };

  const NewJobButton = () => (
    <Link href="/jobs/new">
      <Button className="rounded-full space-x-2">
        <Plus className="size-4" />
        <div>New Job</div>
      </Button>
    </Link>
  );

  return (
    <FullWidthPageLayout title="Jobs" button={<NewJobButton />}>
      <Tabs defaultValue={TabNames.jobs}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value={TabNames.jobs}>{TabNames.jobs}</TabsTrigger>
          <TabsTrigger value={TabNames.runs}>{TabNames.runs}</TabsTrigger>
        </TabsList>
        <TabsContent value={TabNames.jobs}>
          {jobs.status === "fulfilled" ? (
            <JobsList jobs={jobs.value} />
          ) : (
            <div>Something went wrong</div>
          )}
        </TabsContent>
        <TabsContent value={TabNames.runs}>
          {runs.status === "fulfilled" ? (
            <RunsList runs={runs.value} />
          ) : (
            <div>Something went wrong</div>
          )}
        </TabsContent>
      </Tabs>
    </FullWidthPageLayout>
  );
}
