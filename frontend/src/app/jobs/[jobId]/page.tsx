"use client";

import {
  type Job,
  type JobAnalytics,
  type PaginatedResponse,
  type Run,
  getJob,
  getJobAnalytics,
  getRunsForJob,
} from "@/app/actions/actions";
import JobIdPage from "@/components/jobs/id/job-id-page";
import FullWidthPageLayout from "@/components/layout/FullWidthPageLayout";
import { Button } from "@/components/ui/button";
import { Edit, Loader2, Play } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

type JobPageProps = {
  params: { jobId: string };
  searchParams: { page?: number; pageSize?: number };
};

export default function JobPage({ params, searchParams }: JobPageProps) {
  const { jobId } = params;
  const page = Number(searchParams.page || 1);
  const pageSize = Number(searchParams.pageSize || 5);
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

  const RunNowButton = () => {
    return (
      <Button
        className="rounded-full"
        onClick={() => {
          console.log("Run job");
        }}
      >
        <Play className="w-4 h-4 mr-2" />
        Run Now
      </Button>
    );
  };

  const EditJobButton = () => {
    return (
      <Button asChild variant="outline" className="rounded-full">
        <Link href={`/jobs/${jobId}/edit`}>
          <div className="flex items-center gap-2">
            <Edit className="w-4 h-4" />
            Edit Job
          </div>
        </Link>
      </Button>
    );
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
  }, [pathname, jobId, page, pageSize]);

  if (!job || !paginatedRuns || !jobAnalytics) {
    return (
      <FullWidthPageLayout
        button={<RunNowButton />}
        secondaryButton={<EditJobButton />}
      >
        <div className="flex justify-center items-center h-full">
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
      </FullWidthPageLayout>
    );
  }

  return (
    <FullWidthPageLayout
      title={job.name}
      button={<RunNowButton />}
      secondaryButton={<EditJobButton />}
    >
      <JobIdPage
        job={job}
        paginatedRuns={paginatedRuns}
        page={page}
        pageSize={pageSize}
        jobAnalytics={jobAnalytics}
      />
    </FullWidthPageLayout>
  );
}
