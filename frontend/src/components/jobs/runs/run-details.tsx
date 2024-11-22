import type { Run } from "@/app/actions/actions";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import dayjs from "dayjs";
import { capitalize } from "lodash";
import { CheckCircle2, CircleX } from "lucide-react";

type RunDetailsProps = {
  run: Run;
};

export default function RunDetails({ run }: RunDetailsProps) {
  const hasSucceeded = run.status === "SUCCESS";

  return (
    <Card>
      <CardHeader>
        <CardTitle>Run Details</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm font-medium text-muted-foreground">Status</p>
            <div className="flex items-center gap-2">
              {hasSucceeded ? (
                <CheckCircle2 className="w-4 h-4 text-green-500" />
              ) : (
                <CircleX className="w-4 h-4 text-red-500" />
              )}
              <p className="text-sm">{capitalize(run.status)}</p>
            </div>
          </div>
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
                ? `${dayjs(run.date_done).diff(run.date_created, "seconds") + 4}s`
                : "Running..."}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">
              Triggered By
            </p>
            <p className="text-sm">{"Scheduled"}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
