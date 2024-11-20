import type { Run } from "@/app/actions/actions";

export default function RunCard({ run }: { run: Run }) {
  return <div>{run.id}</div>;
}
