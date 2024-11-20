import { getJob } from "@/app/actions/actions";
import JobIdPage from "@/components/jobs/id/job-id-page";

export default async function JobPage({ params }: { params: { id: string } }) {
  const job = await getJob(params.id);
  return <JobIdPage job={job} />;
}
