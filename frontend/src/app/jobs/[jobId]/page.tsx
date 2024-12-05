"use client";

import {
  type Job,
  type JobAnalytics,
  type PaginatedResponse,
  type Run,
  deleteJob,
  getJob,
  getJobAnalytics,
  getRunsForJob,
  startJob,
} from "@/app/actions/actions";
import JobIdPage from "@/components/jobs/id/job-id-page";
import FullWidthPageLayout from "@/components/layout/FullWidthPageLayout";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Edit, Loader2, MoreHorizontal, Play, Trash2 } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { memo, useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";

type JobPageProps = {
  params: { jobId: string };
  searchParams: { page?: number; pageSize?: number };
};

const RunNowButton = memo(({ jobId }: { jobId: string }) => {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleRunNow = async () => {
    setIsLoading(true);
    try {
      const job = await startJob(jobId);
      if (job) {
        toast.success("Job started");
        router.refresh();
      } else {
        toast.error("Failed to start job");
      }
    } catch (error) {
      toast.error("Failed to start job");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      className="rounded-full"
      onClick={handleRunNow}
      disabled={isLoading}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
      ) : (
        <Play className="w-4 h-4 mr-2" />
      )}
      Run Now
    </Button>
  );
});

const JobActions = memo(({ jobId }: { jobId: string }) => {
  const router = useRouter();

  const handleDelete = async () => {
    const success = await deleteJob(jobId);
    if (success) {
      toast.success("Job deleted");
      router.push("/jobs");
    } else {
      toast.error("Failed to delete job");
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon" className="rounded-full">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem asChild>
          <Link href={`/jobs/${jobId}/edit`}>
            <Edit className="w-4 h-4 mr-2" />
            <span>Edit Job</span>
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <div onClick={handleDelete}>
            <Trash2 className="w-4 h-4 mr-2" />
            <span>Delete</span>
          </div>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
});

export default function JobPage({ params, searchParams }: JobPageProps) {
  const { jobId } = params;
  const page = Number(searchParams.page || 1);
  const pageSize = Number(searchParams.pageSize || 10);
  const pathname = usePathname();

  const [job, setJob] = useState<Job | null>(null);
  const [paginatedRuns, setPaginatedRuns] =
    useState<PaginatedResponse<Run> | null>(null);
  const [jobAnalytics, setJobAnalytics] = useState<JobAnalytics | null>(null);

  const pollingInterval = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef<boolean>(true);

  const fetchData = async () => {
    if (!isMountedRef.current) return;

    const [jobData, runsData, analyticsData] = await Promise.all([
      getJob(jobId),
      getRunsForJob({
        jobId: jobId,
        page,
        pageSize,
      }),
      getJobAnalytics(jobId),
    ]);

    if (!isMountedRef.current) return;

    setJob(jobData);
    setPaginatedRuns(runsData);
    setJobAnalytics(analyticsData);
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
  }, [pathname, jobId, page, pageSize]);

  const memoizedJob = useMemo(() => job, [job]);
  const memoizedPaginatedRuns = useMemo(() => paginatedRuns, [paginatedRuns]);

  if (!memoizedJob || !memoizedPaginatedRuns || !jobAnalytics) {
    return (
      <FullWidthPageLayout
        button={<RunNowButton jobId={jobId} />}
        secondaryButton={<JobActions jobId={jobId} />}
      >
        <div className="flex justify-center items-center h-full">
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
      </FullWidthPageLayout>
    );
  }

  return (
    <FullWidthPageLayout
      title={memoizedJob.name}
      button={<RunNowButton jobId={jobId} />}
      secondaryButton={<JobActions jobId={jobId} />}
    >
      <JobIdPage
        job={memoizedJob}
        paginatedRuns={memoizedPaginatedRuns}
        page={page}
        pageSize={pageSize}
        jobAnalytics={jobAnalytics}
      />
    </FullWidthPageLayout>
  );
}
