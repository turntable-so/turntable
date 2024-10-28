"use client";

import useSession from "@/app/hooks/use-session";
import useWorkflowUpdates from "@/app/hooks/use-workflow-updates";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import React, { useEffect } from "react";
import { getResourceIcon } from "../../lib/utils";
import { Badge } from "../ui/badge";
import { Card, CardDescription, CardHeader, CardTitle } from "../ui/card";

dayjs.extend(relativeTime);

type Resource = {
  id: string;
  name: string;
  updated_at: string;
  type: string;
  last_synced: string;
  status: string;
  subtype: string;
  has_dbt: boolean;
};

export default function ConnectionCard({
  resource,
}: {
  resource: Resource;
}) {
  const session = useSession();
  const router = useRouter();
  const [realStatus, setRealStatus] = React.useState(resource.status);

  const [status, resourceId] = useWorkflowUpdates(
    session.user.current_workspace.id,
  );

  useEffect(() => {
    if (resourceId === resource.id) {
      setRealStatus(status);
    }
  }, [status, resourceId, resource]);

  return (
    <Card
      className="rounded-md hover:border-black hover:cursor-pointer"
      onClick={() => {
        router.push(`/connections/${resource.id}`);
      }}
    >
      <CardHeader>
        <div className="flex items-center space-x-4">
          <div className="mb-1 space-y-1">
            {getResourceIcon(resource.subtype)}
            {resource.has_dbt && getResourceIcon("dbt")}
          </div>
          <div className="w-full flex justify-between items-center">
            <div className="space-y-1">
              <CardTitle>{resource.name}</CardTitle>
              {resource.last_synced ? (
                <CardDescription>{`Synced ${dayjs(resource.last_synced).fromNow()} `}</CardDescription>
              ) : (
                <CardDescription>{`Not synced`}</CardDescription>
              )}
            </div>

            <div className="float-right space-y-0">
              <div className="flex justify-end items-center space-x-2">
                <div>
                  {realStatus === "RUNNING" && (
                    <Badge
                      variant="secondary"
                      className="flex space-x-2 items-center font-medium text-sm"
                    >
                      <Loader2 className="h-3 w-3 animate-spin opacity-50" />
                      <div>Syncing </div>
                    </Badge>
                  )}
                  {realStatus === "FAILED" && (
                    <Badge
                      variant="secondary"
                      className="flex space-x-2 items-center font-medium text-sm"
                    >
                      <div className="w-2 h-2 rounded-full bg-red-500"></div>
                      <div>Failed to sync </div>
                    </Badge>
                  )}
                  {realStatus === "SUCCESS" && (
                    <Badge
                      variant="secondary"
                      className="flex space-x-2 items-center font-medium text-sm"
                    >
                      <div className="w-2 h-2 rounded-full bg-green-500"></div>
                      <div>Connected </div>
                    </Badge>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardHeader>
    </Card>
  );
}
