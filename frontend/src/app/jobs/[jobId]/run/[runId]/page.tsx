import { getJob, getRun } from "@/app/actions/actions";
import JobRunIdPage from "@/components/jobs/runs/job-run-id-page";

type JobRunPageProps = {
  params: { jobId: string; runId: string };
};

export default async function JobRunPage({ params }: JobRunPageProps) {
  const runPromise = getRun(params.runId);
  const jobPromise = getJob(params.jobId);

  const [run, job] = await Promise.all([runPromise, jobPromise]);

  return <JobRunIdPage run={run} job={job} />;
}
