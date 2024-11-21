import { getJob } from "@/app/actions/actions";
import JobIdPage from "@/components/jobs/id/job-id-page";

type JobPageProps = {
  params: { id: string };
};

export default async function JobPage({ params }: JobPageProps) {
  const job = await getJob(params.id);
  // const runHistory = await getRunHistoryForJob();
  // const recentRuns = await getRecentRunsForJob();

  if (!job) {
    return <div>Job not found</div>;
  }

  console.log("job: ", job);

  return <JobIdPage job={job} />;
}
