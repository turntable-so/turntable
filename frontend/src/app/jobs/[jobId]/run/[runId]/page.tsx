"use client";

import { Loader2, RefreshCw } from "lucide-react";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import {
  type Job,
  type RunWithJob,
  getJob,
  getRun,
} from "@/app/actions/actions";
import JobRunIdPage from "@/components/jobs/runs/job-run-id-page";
import FullWidthPageLayout from "@/components/layout/FullWidthPageLayout";
import { Button } from "@/components/ui/button";
import { truncateUuid } from "@/lib/id-utils";

type JobRunPageProps = {
  params: { jobId: string; runId: string };
};

export default function JobRunPage({ params }: JobRunPageProps) {
  const { jobId, runId } = params;
  const pathname = usePathname();

  const [run, setRun] = useState<RunWithJob | null>(null);
  const [job, setJob] = useState<Job | null>(null);

  const pollingInterval = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef<boolean>(true);

  const fetchData = async () => {
    if (!isMountedRef.current) return;

    const [runData, jobData] = await Promise.all([
      getRun(runId),
      getJob(jobId),
    ]);

    if (!isMountedRef.current) return;

    setRun(runData);
    setJob(jobData);
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

  useEffect(() => {
    isMountedRef.current = true;

    // Initial fetch
    fetchData();

    // Set up polling interval to fetch data every 3 seconds
    pollingInterval.current = setInterval(fetchData, 3000);

    return () => {
      // Cleanup function to prevent memory leaks
      isMountedRef.current = false;
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
        pollingInterval.current = null;
      }
    };
  }, [pathname, jobId, runId]);

  if (!run || !job) {
    // Return a loading indicator or skeleton
    return (
      <FullWidthPageLayout title={""} button={<RunAgainButton />}>
        <div className="flex justify-center items-center h-full">
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
      </FullWidthPageLayout>
    );
  }

  return (
    <FullWidthPageLayout
      title={`${job.name} / Run ${truncateUuid(run.task_id)}`}
      button={<RunAgainButton />}
    >
      <JobRunIdPage run={run} job={job} />
    </FullWidthPageLayout>
  );
}
