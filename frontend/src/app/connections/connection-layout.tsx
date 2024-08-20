
'use client';

import { BigQueryLogo } from '@/components/connections/connection-options';
import BigqueryForm from "@/components/connections/forms/bigquery-form";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LoaderButton } from "@/components/ui/LoadingSpinner";
import { Separator } from "@/components/ui/separator";
import { ChevronLeft } from "lucide-react";

import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import { useRouter } from "next/navigation";

dayjs.extend(relativeTime)

import useSession from '@/app/hooks/use-session';
import useWorkflowUpdates from '@/app/hooks/use-workflow-updates';
import DbtProjectForm from '@/components/connections/forms/dbt-project-form';
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
import { PostgresLogo } from "../../lib/utils";
import { deleteResource, syncResource } from "../actions/actions";

type DbtDetails = {
    git_repo_url: string
    main_git_branch: string
    project_path: string
    threads: number
    version: string
    database: string
    schema: string
}

export default function ConnectionLayout({ resource, details, dbtDetails }: { resource?: any, details?: any, dbtDetails?: DbtDetails }) {
    const router = useRouter()
    const session = useSession()

    const workflowUpdates = useWorkflowUpdates(session.user.current_workspace.id)

    console.log({ resource, details, dbtDetails })


    return (
        <div className='max-w-7xl w-full px-16 py-4'>
            <Button variant='ghost' className='my-4 text-lg  flex items-center space-x-4' onClick={() => {
                router.push('/connections')
            }}>
                <ChevronLeft className='size-5' />
                <div className='flex space-x-2 items-center'>
                    {resource.subtype === 'bigquery' && <BigQueryLogo />}
                    {resource.subtype === 'postgres' && <PostgresLogo />}
                    <div>Edit {resource.name}</div>
                </div>
            </Button>
            <Separator />
            <div className='flex justify-center mb-16'>
                <div className='flex-col justify-center w-full max-w-2xl py-8 space-y-8'>
                    <Card className='px-3 py-6 flex justify-between'>
                        <div>
                            <CardTitle>Sync Connection</CardTitle>
                            <CardDescription className='py-1'>{`Last synced ${dayjs(resource.updated_at).fromNow()} `}</CardDescription>
                        </div>
                        <Button onClick={() => {
                            const syncResourceAndRefresh = async () => {
                                const res = await syncResource(resource.id)
                                if (res.success) {
                                    router.replace('/connections/' + resource.id)
                                }
                            }
                            syncResourceAndRefresh()
                        }} variant='secondary' > Run Sync</Button>
                    </Card>
                    <Card className='py-6'>
                        <CardHeader>
                            <CardTitle className="text-xl">
                                Connection Details
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            {resource.subtype === 'bigquery' && <BigqueryForm resource={resource} details={details} />}
                            {resource.subtype === 'postgres' && <PostgresForm resource={resource} details={details} />}
                        </CardContent>
                    </Card>
                    {dbtDetails && (
                        <DbtProjectForm resource={resource} details={dbtDetails} />
                    )}
                    <div className='h-4' />
                    <Card className='flex justify-between px-3 py-6 border-red-300'>
                        <div>
                            <CardTitle>Delete Connection</CardTitle>
                            <CardDescription className='py-1'>Warning: this cannot be undone</CardDescription>
                        </div>
                        <AlertDialog>
                            <AlertDialogTrigger asChild>
                                <Button variant='destructive'>Delete</Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                                <AlertDialogHeader>
                                    <AlertDialogDescription>
                                        <span>Are you sure you want to delete </span><span className='font-bold'>{resource.name}</span><span>?</span>
                                    </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                                    <LoaderButton variant='destructive' onClick={() => {
                                        async function deleteApi(resourceId: string) {
                                            const res = await deleteResource(resourceId)
                                            if (res.success) {
                                                router.push('/connections')
                                            }
                                        }
                                        if (resource) {
                                            deleteApi(resource.id)
                                        }
                                    }}>
                                        Yes, Delete Connection
                                    </LoaderButton>
                                </AlertDialogFooter>
                            </AlertDialogContent>
                        </AlertDialog>

                    </Card>
                </div>
            </div>
        </div >
    )
}