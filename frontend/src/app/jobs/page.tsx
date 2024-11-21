import { Plus } from "lucide-react";
import FullWidthPageLayout from "../../components/layout/FullWidthPageLayout";

import { Button } from "@/components/ui/button";
import Link from "next/link";
import {
  getPaginatedJobs,
  getPaginatedRuns,
  PaginatedResponse,
  type Job,
  type Run,
} from "../actions/actions";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import JobsList from "@/components/jobs/jobs-list";
import RunsList from "@/components/jobs/runs-list";

type JobsPageProps = {
  searchParams: { type?: "jobs" | "runs"; page?: number; pageSize?: number };
};

export default async function JobsPage({ searchParams }: JobsPageProps) {
  const type = searchParams.type || "jobs";
  const page = Number(searchParams.page || 1);
  const pageSize = Number(searchParams.pageSize || 10);

  const paginationParams = {
    page,
    pageSize,
  };
  const promise =
    type === "jobs"
      ? getPaginatedJobs(paginationParams)
      : getPaginatedRuns(paginationParams);
  const result = await promise;

  const TabNames = { jobs: "Jobs", runs: "Runs" };
  const selectedTab = type === "jobs" ? TabNames.jobs : TabNames.runs;

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
      <Tabs defaultValue={selectedTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value={TabNames.jobs} asChild>
            <Link href={"/jobs"}>{TabNames.jobs}</Link>
          </TabsTrigger>
          <TabsTrigger value={TabNames.runs} asChild>
            <Link href={"/jobs?type=runs"}>{TabNames.runs}</Link>
          </TabsTrigger>
        </TabsList>
        <TabsContent value={TabNames.jobs}>
          {type === "jobs" ? (
            <JobsList
              jobs={(result as PaginatedResponse<Job>).results}
              page={page}
              pageSize={pageSize}
              count={(result as PaginatedResponse<Job>).count}
            />
          ) : null}
        </TabsContent>
        <TabsContent value={TabNames.runs}>
          {type === "runs" ? (
            <RunsList
              runs={(result as PaginatedResponse<Run>).results}
              page={page}
              pageSize={pageSize}
              count={(result as PaginatedResponse<Run>).count}
            />
          ) : null}
        </TabsContent>
      </Tabs>
    </FullWidthPageLayout>
  );
}
