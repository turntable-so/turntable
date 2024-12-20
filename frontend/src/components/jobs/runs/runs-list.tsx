import type { RunWithJob } from "@/app/actions/actions";
import { Fragment } from "react";
import JobRunPagination from "../job-run-pagination";
import RunCard from "./run-card";

type RunsListProps = {
  runs: Array<RunWithJob>;
  page: number;
  pageSize: number;
  count: number;
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
