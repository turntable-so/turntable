import { getJob, getJobAnalytics, getRunsForJob } from "@/app/actions/actions";
import JobIdPage from "@/components/jobs/id/job-id-page";

type JobPageProps = {
  params: { jobId: string };
  searchParams: { page?: number; pageSize?: number };
};

export default async function JobPage({ params, searchParams }: JobPageProps) {
  const page = Number(searchParams.page || 1);
  const pageSize = Number(searchParams.pageSize || 10);

  const jobPromise = getJob(params.jobId);
  const paginatedRunsPromise = getRunsForJob({
    jobId: params.jobId,
    page,
    pageSize,
  });
  const jobAnalyticsPromise = getJobAnalytics(params.jobId);

  const [job, paginatedRuns, jobAnalytics] = await Promise.all([
    jobPromise,
    paginatedRunsPromise,
    jobAnalyticsPromise,
  ]);

  return (
    <JobIdPage
      job={job}
      paginatedRuns={paginatedRuns}
      page={page}
      pageSize={pageSize}
      jobAnalytics={jobAnalytics}
    />
  );
}
