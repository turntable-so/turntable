import type { Run } from "@/app/actions/actions";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import dayjs from "dayjs";
import { Badge } from "lucide-react";

type RunDetailsProps = {
  run: Run;
};

export default function RunDetails({ run }: RunDetailsProps) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "success":
        return "bg-green-500/10 text-green-500";
      case "error":
        return "bg-red-500/10 text-red-500";
      case "running":
        return "bg-blue-500/10 text-blue-500";
      default:
        return "bg-gray-500/10 text-gray-500";
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Run Details</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p>Status</p>
            <Badge className={`${getStatusColor(run.status)}`}>
              {run.status}
            </Badge>
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
        </div>
      </CardContent>
    </Card>
  );
}
