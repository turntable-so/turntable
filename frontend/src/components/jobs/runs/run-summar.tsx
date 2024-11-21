import type { Run } from "@/app/actions/actions";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import dayjs from "dayjs";

type RunSummaryProps = {
  run: Run;
};

export default function RunSummary({ run }: RunSummaryProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Run Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm font-medium text-muted-foreground">
              Started At
            </p>
            <p className="text-sm">
              {dayjs(run.date_created).format("MMM D, YYYY h:mm A")}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">
              Duration
            </p>
            <p className="text-sm">
              {run.date_done
                ? `${dayjs(run.date_done).diff(run.date_created, "seconds")}s`
                : "Running..."}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">
              Triggered By
            </p>
            <p className="text-sm">{"Manual"}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">
              Environment
            </p>
            <p className="text-sm">{"Production"}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
