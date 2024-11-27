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
import dayjs from "dayjs";
import { Loader2, Plus } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

type JobsPageProps = {
  searchParams: {
    page?: number;
    pageSize?: number;
  };
};

export default function JobsPage({ searchParams }: JobsPageProps) {
  const router = useRouter();
  const page = Number(searchParams.page || 1);
  const pageSize = Number(searchParams.pageSize || 10);

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

    const sortedJobs = (jobsData?.results || []).sort((a, b) => {
      if (
        a.latest_run?.status === "STARTED" &&
        b.latest_run?.status !== "STARTED"
      )
        return -1;
      if (
        a.latest_run?.status !== "STARTED" &&
        b.latest_run?.status === "STARTED"
      )
        return 1;
      return dayjs.utc(a.next_run).diff(dayjs.utc(b.next_run));
    });

    const sortedRuns = (runsData?.results || []).sort((a, b) => {
      if (a.status === "STARTED" && b.status !== "STARTED") return -1;
      if (a.status !== "STARTED" && b.status === "STARTED") return 1;
      return dayjs.utc(b.date_done).diff(dayjs.utc(a.date_done));
    });

    setJobsResult({ ...jobsData, results: sortedJobs });
    setRunsResult({ ...runsData, results: sortedRuns });
  };

  useEffect(() => {
    isMountedRef.current = true;

    const startPolling = () => {
      fetchData();
      if (!pollingInterval.current) {
        pollingInterval.current = setInterval(fetchData, 2000);
      }
    };

    const stopPolling = () => {
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
        pollingInterval.current = null;
      }
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        startPolling();
      } else {
        stopPolling();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    // Start polling if the page is visible
    if (document.visibilityState === "visible") {
      startPolling();
    }

    return () => {
      isMountedRef.current = false;
      stopPolling();
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [page, pageSize]);

  const TabNames = { jobs: "Jobs", runs: "Runs" };

  const handleTabChange = (value: string) => {
    router.push("/jobs");
  };

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
      <Tabs defaultValue={TabNames.jobs} onValueChange={handleTabChange}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value={TabNames.jobs}>Jobs</TabsTrigger>
          <TabsTrigger value={TabNames.runs}>Runs</TabsTrigger>
        </TabsList>
        <TabsContent value={TabNames.jobs}>
          <JobsList
            jobs={jobsResult.results || []}
            page={page}
            pageSize={pageSize}
            count={jobsResult.count}
          />
        </TabsContent>
        <TabsContent value={TabNames.runs}>
          <RunsList
            runs={runsResult.results || []}
            page={page}
            pageSize={pageSize}
            count={runsResult.count}
          />
        </TabsContent>
      </Tabs>
    </FullWidthPageLayout>
  );
}
