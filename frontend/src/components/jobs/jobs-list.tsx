"use client";

import type { Job } from "@/app/actions/actions";
import { Fragment } from "react";
import JobCard from "./job-card";
import JobRunPagination from "./job-run-pagination";

type JobsListProps = {
  jobs: Array<Job>;
  page: number;
  pageSize: number;
  count: number;
};

export default function JobsList({
  jobs,
  page,
  pageSize,
  count,
}: JobsListProps) {
  return (
    <div className="flex flex-col space-y-2">
      {jobs.length ? (
        <Fragment>
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
          <JobRunPagination page={page} pageSize={pageSize} count={count} />
        </Fragment>
      ) : (
        <div>No jobs found</div>
      )}
    </div>
  );
}
