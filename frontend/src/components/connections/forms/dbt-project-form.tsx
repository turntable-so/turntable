"use client";

import {
  createResource,
  getSshKey,
  testGitConnection,
  updateResource,
} from "@/app/actions/actions";
import useSession from "@/app/hooks/use-session";
import { LoaderButton } from "@/components/ui/LoadingSpinner";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { useAppContext } from "@/contexts/AppContext";
import { zodResolver } from "@hookform/resolvers/zod";
import { CopyIcon } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import EnvironmentVariables from "../environment-variables";

const DbtCoreConfig = ({
  resources,
  form,
}: { resources: any[]; form: any }) => (
  <Card className="w-full rounded-sm">
    <CardHeader>
      <CardTitle className="text-xl">dbt Core Config</CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <FormField
        control={form.control}
        name="database_resource_id"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Database Connection</FormLabel>
            <Select onValueChange={field.onChange} defaultValue={field.value}>
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select a database connection" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {resources.map((resource: any) => (
                  <SelectItem key={resource.id} value={resource.id}>
                    {resource.name}
                  </SelectItem>
                ))}
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
            <FormControl>
              <Input type="number" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="targetName"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Target Name</FormLabel>
            <FormControl>
              <Input {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="version"
        render={({ field }) => (
          <FormItem>
            <FormLabel>dbt Version</FormLabel>
            <FormControl>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <SelectTrigger>
                  <SelectValue placeholder="Select version" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1.5">1.5</SelectItem>
                  <SelectItem value="1.6">1.6</SelectItem>
                  <SelectItem value="1.7">1.7</SelectItem>
                  <SelectItem value="1.8">1.8</SelectItem>
                </SelectContent>
              </Select>
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <div className="flex items-center">
        <div className="w-1/2 pr-2">
          <FormField
            control={form.control}
            name="database"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Database</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        <div className="w-1/2 pl-2">
          <FormField
            control={form.control}
            name="schema"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Schema</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
      </div>
      <EnvironmentVariables form={form} />
    </CardContent>
  </Card>
);

export default function DbtProjectForm({
  resource,
  details,
}: { resource?: any; details?: any }) {
  const router = useRouter();
  const { resources, fetchResources } = useAppContext();

  const { user } = useSession();
  const [connectionCheckStatus, setConnectionCheckStatus] = useState<
    "PENDING" | "STARTED" | "FAILURE" | "SUCCESS"
  >("PENDING");
  const [selectedTab, setSelectedTab] = useState<"remote" | "local">("remote");

  useEffect(() => {
    fetchResources();
  }, []);

  const RemoteFormSchema = z.object({
    database_resource_id: z.string().min(1, {
      message: "Database can't be empty",
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
    targetName: z.string().optional(),
    deployKey: z.string({
      required_error: "Please enter a Deploy Key",
    }),
    sshKeyId: z.string({
      required_error: "Please enter a Deploy Key",
    }),
    dbtGitRepoUrl: z.string().min(5, {
      message: "Git repo url can't be empty",
    }),
    mainGitBranch: z.string().min(1, {
      message: "Please specify a main branch",
    }),
    subdirectory: z.string().min(1, {
      message: "Please enter a subdirectory (.)",
    }),
    env_vars: z.record(z.string(), z.string()).default({}),
  });

  const LocalFormSchema = z.object({
    database_resource_id: z.string().min(1, {
      message: "Database can't be empty",
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
    subdirectory: z.string().min(1, {
      message: "Please enter a subdirectory",
    }),
    env_vars: z.record(z.string(), z.string()).default({}),
  });

  const remoteForm = useForm<z.infer<typeof RemoteFormSchema>>({
    resolver: zodResolver(RemoteFormSchema),
    defaultValues: {
      database_resource_id: resource?.id || "",
      deployKey: details?.repository?.ssh_key?.public_key || "",
      sshKeyId: details?.repository?.ssh_key?.id || "",
      dbtGitRepoUrl: details?.repository?.git_repo_url || "",
      mainGitBranch: details?.repository?.main_branch_name || "main",
      subdirectory: details?.project_path || ".",
      threads: details?.threads || 1,
      version: details?.version || "",
      database: details?.database || "",
      schema: details?.schema || "",
      targetName: details?.target_name || "",
      env_vars: details?.env_vars || {},
    },
  });

  const localForm = useForm<z.infer<typeof LocalFormSchema>>({
    resolver: zodResolver(LocalFormSchema),
    defaultValues: {
      database_resource_id: resource?.id || "",
      subdirectory: details?.project_path || ".",
      threads: details?.threads || 1,
      version: details?.version || "",
      database: details?.database || "",
      schema: details?.schema || "f",
      env_vars: details?.env_vars || {},
    },
  });

  useEffect(() => {
    const getSshKeyFunction = async (workspace_id: string) => {
      const data = await getSshKey(workspace_id);
      if (data) {
        remoteForm.setValue("deployKey", data.public_key);
        remoteForm.setValue("sshKeyId", data.id);
      }
    };

    if (user?.current_workspace?.id && !details?.deploy_key) {
      getSshKeyFunction(user.current_workspace.id);
    }
  }, [user, user.current_workspace]);

  async function testConnection() {
    setConnectionCheckStatus("STARTED");
    const data = await testGitConnection(
      remoteForm.getValues().deployKey,
      remoteForm.getValues().dbtGitRepoUrl,
    );
    if (data.success === true) {
      setConnectionCheckStatus("SUCCESS");
    } else {
      setConnectionCheckStatus("FAILURE");
    }
  }

  const isUpdate = !!resource?.id;

  async function onSubmit(
    data: z.infer<typeof RemoteFormSchema> | z.infer<typeof LocalFormSchema>,
  ) {
    console.log('Form Data:', data);
    console.log('Environment Variables:', data.env_vars);
    
    const payload = {
      resource: {
        type: "db",
      },
      subtype: "dbt",
      config: {
        resource_id: data.database_resource_id,
        repository: {
          git_repo_url: (data as z.infer<typeof RemoteFormSchema>)
            .dbtGitRepoUrl,
          main_branch_name: (data as z.infer<typeof RemoteFormSchema>)
            .mainGitBranch,
          ssh_key: {
            id: (data as z.infer<typeof RemoteFormSchema>).sshKeyId,
            public_key: (data as z.infer<typeof RemoteFormSchema>).deployKey,
          },
        },
        project_path: data.subdirectory,
        threads: data.threads,
        target_name: (data as z.infer<typeof RemoteFormSchema>).targetName,
        version: data.version,
        database: data.database,
        schema: data.schema,
        env_vars: data.env_vars,
      },
    };
    
    console.log('Submission payload:', payload);
    const res = isUpdate
      ? await updateResource(resource.id, payload)
      : await createResource(payload as any);
    if (res.name !== undefined) {
      if (isUpdate) {
        toast.success("Connection updated");
        return;
      }
      toast.success("Connection created");
      router.push(`/connections/${res.id}`);
    } else {
      toast.error(`Failed to save connection: ${res[0]}`);
    }
  }

  return (
    <div className="w-full max-w-2xl">
      {!resources || resources.length === 0 ? (
        <Card className="py-5">
          <CardTitle className="text-xl">
            <CardContent>Database Connection Required</CardContent>
          </CardTitle>
          <CardContent>
            It looks like you haven&apos;t set up a database connection yet.
            Please connect to a database first and then return to this page to
            connect your dbt project.
          </CardContent>
          <CardFooter>
            <Button
              onClick={() => {
                router.push("/connections/new");
              }}
            >
              Set up Database Connection
            </Button>
          </CardFooter>
        </Card>
      ) : (
        <div className="flex flex-col gap-4">
          <Tabs
            defaultValue="remote"
            onValueChange={(value) =>
              setSelectedTab(value as "remote" | "local")
            }
          >
            <TabsList>
              <TabsTrigger value="remote">Remote Repository</TabsTrigger>
            </TabsList>
            <TabsContent value="remote">
              <Form {...remoteForm}>
                <form
                  onSubmit={remoteForm.handleSubmit(onSubmit)}
                  className="space-y-6 text-black dark:text-white"
                >
                  <Card className="w-full rounded-sm">
                    <CardHeader>
                      <CardTitle className="text-xl">Code Repository</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <FormField
                        control={remoteForm.control}
                        name="deployKey"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Deploy Key</FormLabel>
                            <br />
                            <FormLabel className="text-sm text-muted-foreground">
                              Go to your dbt Git repo, go to Deploy Keys, click
                              Add Deploy Key, and paste this public key. Be sure
                              to give it write access.
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
                                toast.info("ssh key copied to clipboard");
                              }}
                              className="flex items-center space-x-2 text-xs"
                              variant="outline"
                            >
                              <CopyIcon className="h-4 w-4" />
                              <div>Copy ssh key</div>
                            </Button>
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={remoteForm.control}
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
                        control={remoteForm.control}
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
                        control={remoteForm.control}
                        name="subdirectory"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Project subdirectory</FormLabel>
                            <FormControl>
                              <Input
                                placeholder="Subdirectory of your repository that contains your dbt project"
                                {...field}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </CardContent>
                    <CardFooter className="flex justify-end">
                      <div className="float-right flex ">
                        {connectionCheckStatus === "SUCCESS" && (
                          <div className="text-green-500 mt-2 mr-2">
                            Connection successful
                          </div>
                        )}
                        {connectionCheckStatus === "FAILURE" && (
                          <div className="text-red-500  mt-2 mr-2">
                            Connection failed
                          </div>
                        )}
                        <LoaderButton
                          variant="secondary"
                          isLoading={connectionCheckStatus === "STARTED"}
                          isDisabled={connectionCheckStatus === "STARTED"}
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
                  <DbtCoreConfig resources={resources} form={remoteForm} />
                  <div className="flex justify-end">
                    <LoaderButton type="submit">
                      {isUpdate ? "Update dbt Project" : "Add dbt Project"}
                    </LoaderButton>
                  </div>
                </form>
              </Form>
            </TabsContent>
            <TabsContent value="local">
              <Form {...localForm}>
                <form
                  onSubmit={localForm.handleSubmit(onSubmit)}
                  className="space-y-6 text-black dark:text-white"
                >
                  <Card className="w-full rounded-sm">
                    <CardHeader>
                      <CardTitle className="text-xl">Local Directory</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <FormField
                        control={localForm.control}
                        name="subdirectory"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Project directory</FormLabel>
                            <CardDescription>
                              Note: If using Docker, Make sure this path is
                              mounted as a volume in the container. This should
                              be the full path where there is a dbt_project.yaml
                              at the root.
                            </CardDescription>
                            <FormControl>
                              <Input
                                placeholder="Directory of your repository that contains your dbt project"
                                {...field}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </CardContent>
                  </Card>
                  <DbtCoreConfig resources={resources} form={localForm} />
                  <div className="flex justify-end">
                    <LoaderButton type="submit">
                      {isUpdate ? "Update dbt Project" : "Add dbt Project"}
                    </LoaderButton>
                  </div>
                </form>
              </Form>
            </TabsContent>
          </Tabs>
        </div>
      )}
    </div>
  );
}
