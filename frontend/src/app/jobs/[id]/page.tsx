import { getJob, getJobAnalytics, getRunsForJob } from "@/app/actions/actions";
import JobIdPage from "@/components/jobs/id/job-id-page";

type JobPageProps = {
  params: { id: string };
  searchParams: { page?: number; pageSize?: number };
};

export default async function JobPage({ params, searchParams }: JobPageProps) {
  const page = Number(searchParams.page || 1);
  const pageSize = Number(searchParams.pageSize || 10);

  const jobPromise = getJob(params.id);
  const paginatedRunsPromise = getRunsForJob({
    jobId: params.id,
    page,
    pageSize,
  });
  const jobAnalyticsPromise = getJobAnalytics(params.id);

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
