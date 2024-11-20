import type { Job } from "@/app/actions/actions";
import JobCard from "./job-card";

type JobsListProps = {
  jobs: Array<Job>;
};

export default function JobsList({ jobs }: JobsListProps) {
  return (
    <div className="flex flex-col space-y-2">
      {jobs.length ? (
        jobs.map((job) => <JobCard key={job.id} job={job} />)
      ) : (
        <div>No jobs found</div>
      )}
    </div>
  );
}
