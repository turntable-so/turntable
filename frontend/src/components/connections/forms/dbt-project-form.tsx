'use client'
import { createResource, getSshKey, testGitConnection, updateResource } from "@/app/actions/actions";
import useSession from "@/app/hooks/use-session";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { LoaderButton } from "@/components/ui/LoadingSpinner";
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useAppContext } from "@/contexts/AppContext";
import { zodResolver } from "@hookform/resolvers/zod";
import { CopyIcon } from "lucide-react";
import { useRouter } from 'next/navigation';
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";


const FormSchema = z.object({
    database_resource_id: z.string().min(1, {
        message: "Database can't be empty",
    }),
    deployKey: z.string({
        required_error: "Please enter a Deploy Key",
    }),
    dbtGitRepoUrl: z.string().min(5, {
        message: "Git repo url can't be empty",
    }),
    mainGitBranch: z.string().min(1, {
        message: "Please specify a main branch",
    }),
    subdirectory: z.string().min(1, {
        message: "Please enter a subdirectory (/)",
    }),
    threads: z.coerce.number().min(1, {
        message: "Threads can't be empty",
    }),
    version: z.string().min(1, {
        message: "Version can't be empty",
    }),
    database: z.string().min(1, {
        message: "Database can't be empty",
    }),
    schema: z.string().min(1, {
        message: "Schema can't be empty",
    }),
})

export default function DbtProjectForm({ resource, details }: { resource?: any, details?: any }) {
    const router = useRouter()
    const { resources } = useAppContext()
    const { user } = useSession()
    console.log({ user })
    const [connectionCheckStatus, setConnectionCheckStatus] = useState<'IDLE' | 'RUNNING' | 'FAIL' | 'SUCCESS'>('IDLE');
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

    console.log({ resource })
    const form = useForm<z.infer<typeof FormSchema>>({
        resolver: zodResolver(FormSchema),
        defaultValues: {
            database_resource_id: resource?.id || "",
            deployKey: details?.deploy_key || "",
            dbtGitRepoUrl: details?.git_repo_url || "",
            mainGitBranch: details?.main_git_branch || "main",
            subdirectory: details?.project_path || '.',
            threads: details?.threads || 1,
            version: details?.version || '',
            database: details?.database || '',
            schema: details?.schema || "",

        },
    })

    useEffect(() => {
        const getSshKeyFunction = async (workspace_id: string) => {
            const data = await getSshKey(workspace_id);
            if (data) {
                form.setValue('deployKey', data.public_key)
            }
        };

        if (user?.current_workspace?.id && !details?.deploy_key) {
            getSshKeyFunction(user.current_workspace.id);
        }
    }, [user, user.current_workspace]);


    async function testConnection() {
        setConnectionCheckStatus('RUNNING')
        const data = await testGitConnection(
            form.getValues().deployKey,
            form.getValues().dbtGitRepoUrl
        );
        console.log({ data })
        if (data.success === true) {
            setConnectionCheckStatus('SUCCESS');
        } else {
            setConnectionCheckStatus('FAIL');
        }
    }

    const isUpdate = resource?.id ? true : false
    console.log({ isUpdate })



    async function onSubmit(data: z.infer<typeof FormSchema>) {
        const payload = {
            resource: {
                type: 'db',
            },
            subtype: 'dbt',
            config: {
                "deploy_key": data.deployKey,
                "resource_id": data.database_resource_id,
                "git_repo_url": data.dbtGitRepoUrl,
                "main_git_branch": data.mainGitBranch,
                "project_path": data.subdirectory,
                "threads": data.threads,
                "version": data.version,
                "database": data.database,
                "schema": data.schema
            }
        }
        const res = isUpdate ? await updateResource(resource.id, payload) : await createResource(payload as any)
        if (res.ok && resource?.id) {
            toast.success('Connection updated')
            router.push(`/connections/${resource.id}`)
        }
        else if (res.id) {
            router.push(`/connections/`)
        }
    }


    return (
        <div className='w-full max-w-2xl'>
            {(!resources || resources.length === 0) ? (
                <Card className='py-5'>
                    <CardTitle className='text-xl'>
                        <CardContent>
                            Database Connection Required
                        </CardContent>
                    </CardTitle>
                    <CardContent>
                        It looks like you haven&apos;t set up a database connection yet. Please connect to a database first and then return to this page to connect your dbt project.
                    </CardContent>
                    <CardFooter>
                        <Button onClick={() => {
                            router.push('/connections/new')
                        }}>Set up Database Connection</Button>
                    </CardFooter>
                </Card>
            ) : (
                < Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 text-black">

                        <Card className="w-full rounded-sm">
                            <CardHeader>
                                <CardTitle className="text-xl">
                                    Code Repository
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <FormField
                                    control={form.control}
                                    name="deployKey"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Deploy Key</FormLabel>
                                            <br />
                                            <FormLabel className="text-sm text-muted-foreground">
                                                Go to your dbt Git repo, go to Deploy Keys, click Add Deploy
                                                Key, and paste this public key. Be sure to give it write
                                                access.
                                            </FormLabel>
                                            <FormControl>
                                                <Textarea
                                                    placeholder="ssh key"
                                                    {...field}
                                                    defaultValue={field.value}
                                                    rows={8}
                                                    disabled={true}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                            <Button
                                                onClick={(event) => {
                                                    event.preventDefault();
                                                    navigator.clipboard.writeText(field.value);
                                                    toast.info('ssh key copied to clipboard')
                                                }}
                                                className="flex items-center space-x-2 text-xs"
                                                variant="outline"
                                            >
                                                <CopyIcon className='h-4 w-4' />
                                                <div>Copy ssh key</div>
                                            </Button>
                                        </FormItem>
                                    )}
                                />
                                <FormField
                                    control={form.control}
                                    name="dbtGitRepoUrl"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>dbt Git Repo URL</FormLabel>
                                            <FormControl>
                                                <Input
                                                    placeholder="git@github.com:org/dbt.git"
                                                    {...field}
                                                    defaultValue={field.value}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                                <FormField
                                    control={form.control}
                                    name="mainGitBranch"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Main Git Branch</FormLabel>
                                            <FormControl>
                                                <Input placeholder="master or main" {...field} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                                <FormField
                                    control={form.control}
                                    name="subdirectory"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Project subdirectory</FormLabel>
                                            <FormControl>
                                                <Input placeholder="Subdirectory of your repository that contains your dbt project" {...field} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                            </CardContent>
                            <CardFooter className="flex justify-end">
                                <div className="float-right flex ">
                                    {connectionCheckStatus === 'SUCCESS' && (
                                        <div className="text-green-500 mt-2 mr-2">Connection successful</div>
                                    )}
                                    {connectionCheckStatus === 'FAIL' && (
                                        <div className="text-red-500  mt-2 mr-2">Connection failed</div>
                                    )}
                                    <LoaderButton
                                        variant='secondary'
                                        isLoading={connectionCheckStatus === 'RUNNING'}
                                        isDisabled={connectionCheckStatus === 'RUNNING'}
                                        onClick={(event) => {
                                            event.preventDefault();
                                            testConnection();
                                        }}
                                    >
                                        Test Connection
                                    </LoaderButton>
                                </div>
                            </CardFooter>
                        </Card>

                        <Card className="w-full rounded-sm">
                            <CardHeader>
                                <CardTitle className="text-xl">
                                    dbt Core Config
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex space-x-8">
                                    <FormField
                                        control={form.control}
                                        name="version"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>dbt Version</FormLabel>
                                                <Select onValueChange={field.onChange} value={field.value}>
                                                    <SelectTrigger className="w-[180px]">
                                                        <SelectValue placeholder="Select a version" />
                                                    </SelectTrigger>
                                                    <SelectContent>
                                                        <SelectGroup>
                                                            {['1.3', '1.4', '1.5', '1.6', '1.7',].map((version: string) => (
                                                                <SelectItem key={version} value={version}>{version}</SelectItem>
                                                            ))}
                                                        </SelectGroup>
                                                    </SelectContent>
                                                </Select>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />
                                    <FormField
                                        control={form.control}
                                        name="threads"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>Threads</FormLabel>
                                                <Input type='number' {...field} />
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />
                                </div>
                                <FormField
                                    control={form.control}
                                    name="database_resource_id"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Attach to an existing database connection</FormLabel>
                                            <Select onValueChange={field.onChange} value={field.value}>
                                                <SelectTrigger className="w-[300px]">
                                                    <SelectValue placeholder="Select a database" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectGroup>
                                                        {resources.map((resource: any) => (
                                                            <SelectItem key={resource.id} value={resource.id}>{resource.name}</SelectItem>
                                                        ))}
                                                    </SelectGroup>
                                                </SelectContent>
                                            </Select>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                                <div className='flex items-center space-x-7'>
                                    <FormField
                                        control={form.control}
                                        name="database"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>Project Database</FormLabel>
                                                <FormControl>
                                                    <Input placeholder="mydb" {...field} />
                                                </FormControl>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />
                                    <FormField
                                        control={form.control}
                                        name="schema"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>Project Schema</FormLabel>
                                                <FormControl>
                                                    <Input placeholder="schema.analytics" {...field} />
                                                </FormControl>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />
                                </div>
                            </CardContent>
                        </Card>


                        <div className='flex justify-end'>
                            <LoaderButton type='submit'>
                                {isUpdate ? 'Update dbt Project' : 'Add dbt Project'}

                            </LoaderButton>
                        </div>
                    </form>
                </Form >
            )
            }
        </div >
    )
}