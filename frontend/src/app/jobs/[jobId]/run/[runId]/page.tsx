"use client";

import {
  type Job,
  type RunWithJob,
  getJob,
  getRun,
} from "@/app/actions/actions";
import JobRunIdPage from "@/components/jobs/runs/job-run-id-page";
import FullWidthPageLayout from "@/components/layout/FullWidthPageLayout";
import { truncateUuid } from "@/lib/id-utils";
import { Loader2 } from "lucide-react";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

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

    if (document.visibilityState === "visible") {
      startPolling();
    }

    return () => {
      isMountedRef.current = false;
      stopPolling();
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [pathname, jobId, runId]);

  if (!run || !job) {
    return (
      <FullWidthPageLayout title={""}>
        <div className="flex justify-center items-center h-full">
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
      </FullWidthPageLayout>
    );
  }

  return (
    <FullWidthPageLayout
      title={`${job.name} / Run ${truncateUuid(run.task_id)}`}
    >
      <JobRunIdPage run={run} job={job} />
    </FullWidthPageLayout>
  );
}
