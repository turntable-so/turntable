import type { Run } from "@/app/actions/actions";
import RunCard from "./run-card";
import { Fragment } from "react";
import JobRunPagination from "./job-run-pagination";

type RunsListProps = {
  runs: Array<Run>;
  page: number;
  pageSize: number;
  count: number;
  jobId: string;
};

export default function RunsList({
  runs,
  page,
  pageSize,
  count,
}: RunsListProps) {
  return (
    <div className="flex flex-col space-y-2 w-full">
      {runs.length ? (
        <Fragment>
          {runs.map((run) => (
            <RunCard key={run.task_id} run={run} />
          ))}
          <JobRunPagination page={page} pageSize={pageSize} count={count} />
        </Fragment>
      ) : (
        <div>No runs found</div>
      )}
    </div>
  );
}
