"use client";

import { BigQueryLogo, DatabricksLogo, RedshiftLogo, SnowflakeLogo, TableauLogo } from "@/components/connections/connection-options";
import BigqueryForm from "@/components/connections/forms/bigquery-form";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { LoaderButton } from "@/components/ui/LoadingSpinner";
import { Separator } from "@/components/ui/separator";
import { ChevronLeft, Loader2 } from "lucide-react";

import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import { useRouter } from "next/navigation";
import { testResource } from "@/app/actions/actions";

dayjs.extend(relativeTime);

import useSession from "@/app/hooks/use-session";
import useWorkflowUpdates from "@/app/hooks/use-workflow-updates";
import DbtProjectForm from "@/components/connections/forms/dbt-project-form";
import MetabaseForm from "@/components/connections/forms/metabase-form";
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import PostgresForm from "../../components/connections/forms/postgres-form";
import { MetabaseIcon, PostgresLogo } from "../../lib/utils";
import { deleteResource, syncResource } from "../actions/actions";
import React, { useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import SnowflakeForm from "@/components/connections/forms/snowflake-form";
import DatabricksForm from "@/components/connections/forms/databricks-form";
import TableauForm from "@/components/connections/forms/tableau-form";
import RedshiftForm from "@/components/connections/forms/redshift-form";

type DbtDetails = {
  git_repo_url: string;
  main_git_branch: string;
  project_path: string;
  threads: number;
  version: string;
  database: string;
  schema: string;
};

export default function ConnectionLayout({
  resource,
  details,
  dbtDetails,
}: {
  resource?: any;
  details?: any;
  dbtDetails?: DbtDetails;
}) {
  const router = useRouter();
  const session = useSession();
  const [realStatus, setRealStatus] = React.useState(resource.status);
  const [testStatus, setTestStatus] = React.useState(true);
  const [testRun, setTestRun] = React.useState(false);

  const [status, resourceId] = useWorkflowUpdates(
    session.user.current_workspace.id
  );

  useEffect(() => {
    if (resourceId === resource.id) {
      setRealStatus(status);
    }
  }, [status, resourceId]);

  const testConnection = async (resource: any) => {
    const tests = await testResource(resource.id);
    setTestRun(true)
    setTestStatus(tests.test_datahub.success && tests.test_db.success)
    return tests;
  }

  return (
    <div className="max-w-7xl w-full px-16 py-4">
      <Button
        variant="ghost"
        className="my-4 text-lg  flex items-center space-x-4"
        onClick={() => {
          router.push("/connections");
        }}
      >
        <ChevronLeft className="size-5" />
        <div className="flex space-x-2 items-center">
          {resource.subtype === "bigquery" && <BigQueryLogo />}
          {resource.subtype === "postgres" && <PostgresLogo />}
          {resource.subtype === "metabase" && <MetabaseIcon />}
          {resource.subtype === "snowflake" && <SnowflakeLogo />}
          {resource.subtype === "databricks" && <DatabricksLogo height={24} width={24} />}
          {resource.subtype === "tableau" && <TableauLogo />}
          {resource.subtype === "redshift" && <RedshiftLogo />}
          <div>Edit {resource.name}</div>
        </div>
      </Button>
      <Separator />
      <div className="flex justify-center mb-16">
        <div className="flex-col justify-center w-full max-w-2xl py-8 space-y-8">
          <Card className="px-5 py-6 flex justify-between items-center">
            <div>
              <CardTitle>Sync Connection</CardTitle>
              <CardDescription className="py-1">{`Last synced ${dayjs(
                resource.updated_at
              ).fromNow()} `}</CardDescription>
            </div>
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
                  <div className="flex flex-row">
                    <Badge
                      variant="secondary"
                      className="flex space-x-2 items-center font-medium text-sm mr-2"
                    >
                      <div className="w-2 h-2 rounded-full bg-red-500"></div>
                      <div>Failed to sync </div>
                    </Badge>
                  </div>
                )}
                {realStatus === "SUCCESS" && (
                  <div className="flex flex-row">
                    <Badge
                      variant="secondary"
                      className="flex space-x-2 items-center font-medium text-sm mr-2"
                    >
                      <div className="w-2 h-2 rounded-full bg-green-500"></div>
                      <div>Connected </div>
                    </Badge>
                  </div>
                )}

              </div>
              <Button
                disabled={realStatus === "RUNNING"}
                className={`${realStatus === "RUNNING" ? "opacity-50" : ""}`}
                onClick={() => {
                  const syncResourceAndRefresh = async () => {
                    const res = await syncResource(resource.id);
                    if (res.success) {
                      router.replace("/connections/" + resource.id);
                    }
                  };
                  syncResourceAndRefresh();
                }}
                variant="secondary"
              >
                {" "}
                Run Sync
              </Button>
            </div>

          </Card>
          <Card className="py-6">
            <CardHeader>
              <CardTitle className="text-xl">Connection Details</CardTitle>
            </CardHeader>
            <CardContent>
              {resource.subtype === "bigquery" && (
                <BigqueryForm resource={resource} details={details} testConnection={testConnection} tested={testRun} connectionCheck={testStatus} />
              )}
              {resource.subtype === "postgres" && (
                <PostgresForm resource={resource} details={details} testConnection={testConnection} tested={testRun} connectionCheck={testStatus} />
              )}
              {resource.subtype === "metabase" && (
                <MetabaseForm resource={resource} details={details} />
              )}
              {resource.subtype === "snowflake" && (
                <SnowflakeForm resource={resource} details={details} testConnection={testConnection} tested={testRun} connectionCheck={testStatus} />
              )}
              {resource.subtype === "databricks" && (
                <DatabricksForm resource={resource} details={details} testConnection={testConnection} tested={testRun} connectionCheck={testStatus} />
              )}
              {resource.subtype === "tableau" && (
                <TableauForm resource={resource} details={details} />
              )}
              {resource.subtype === "redshift" && (
                <RedshiftForm resource={resource} details={details} />
              )}
            </CardContent>
          </Card>
          {dbtDetails && (
            <DbtProjectForm resource={resource} details={dbtDetails} />
          )}
          <div className="h-4" />
          <Card className="flex justify-between px-3 py-6 border-red-300">
            <div>
              <CardTitle>Delete Connection</CardTitle>
              <CardDescription className="py-1">
                Warning: this cannot be undone
              </CardDescription>
            </div>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive">Delete</Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogDescription>
                    <span>Are you sure you want to delete </span>
                    <span className="font-bold">{resource.name}</span>
                    <span>?</span>
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <LoaderButton
                    variant="destructive"
                    onClick={() => {
                      async function deleteApi(resourceId: string) {
                        const res = await deleteResource(resourceId);
                        if (res.success) {
                          router.push("/connections");
                        }
                      }
                      if (resource) {
                        deleteApi(resource.id);
                      }
                    }}
                  >
                    Yes, Delete Connection
                  </LoaderButton>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </Card>
        </div>
      </div>
    </div>
  );
}
