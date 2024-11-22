"use client";

import {
  type Job,
  type PaginatedResponse,
  type RunWithJob,
  getPaginatedJobs,
  getPaginatedRuns,
} from "@/app/actions/actions";
import JobsList from "@/components/jobs/jobs-list";
import RunsList from "@/components/jobs/runs/runs-list";
import FullWidthPageLayout from "@/components/layout/FullWidthPageLayout";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, Plus } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

type JobsPageProps = {
  searchParams: {
    type?: "jobs" | "runs";
    page?: number;
    pageSize?: number;
  };
};

export default function JobsPage({ searchParams }: JobsPageProps) {
  const type = searchParams.type || "jobs";
  const page = Number(searchParams.page || 1);
  const pageSize = Number(searchParams.pageSize || 5);
  const pathname = usePathname();

  const paginationParams = {
    page,
    pageSize,
  };

  const [jobsResult, setJobsResult] = useState<PaginatedResponse<Job> | null>(
    null,
  );
  const [runsResult, setRunsResult] =
    useState<PaginatedResponse<RunWithJob> | null>(null);

  const pollingInterval = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef<boolean>(true);

  const fetchData = async () => {
    if (!isMountedRef.current) return;

    const [jobsData, runsData] = await Promise.all([
      getPaginatedJobs(paginationParams),
      getPaginatedRuns(paginationParams),
    ]);

    if (!isMountedRef.current) return;

    setJobsResult(jobsData);
    setRunsResult(runsData);
  };

  useEffect(() => {
    isMountedRef.current = true;
    fetchData();
    pollingInterval.current = setInterval(fetchData, 3000);
    return () => {
      isMountedRef.current = false;
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
        pollingInterval.current = null;
      }
    };
  }, [pathname, type, page, pageSize]);

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

  if (!jobsResult || !runsResult) {
    return (
      <FullWidthPageLayout title="Jobs" button={<NewJobButton />}>
        <div className="flex justify-center items-center h-full">
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
      </FullWidthPageLayout>
    );
  }

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
              jobs={jobsResult.results || []}
              page={page}
              pageSize={pageSize}
              count={jobsResult.count}
            />
          ) : null}
        </TabsContent>
        <TabsContent value={TabNames.runs}>
          {type === "runs" ? (
            <RunsList
              runs={runsResult.results || []}
              page={page}
              pageSize={pageSize}
              count={runsResult.count}
            />
          ) : null}
        </TabsContent>
      </Tabs>
    </FullWidthPageLayout>
  );
}
