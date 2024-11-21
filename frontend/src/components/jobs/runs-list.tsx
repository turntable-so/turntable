import type { Run } from "@/app/actions/actions";
import RunCard from "./run-card";

type RunsListProps = {
  runs: Array<Run>;
};

export default function RunsList({ runs }: RunsListProps) {
  return (
    <div className="flex flex-col space-y-2">
      {runs.length ? (
        runs.map((run) => <RunCard key={run.task_id} run={run} />)
      ) : (
        <div>No runs found</div>
      )}
    </div>
  );
}
