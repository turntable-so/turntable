"use client";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import FullWidthPageLayout from "../../../components/layout/FullWidthPageLayout";
import { Button } from "../../../components/ui/button";
import { createGithubConnection, getSshKey, getWorkspace, testGitConnection } from "../../actions/actions";

import { zodResolver } from "@hookform/resolvers/zod";
import { GitHubLogoIcon } from "@radix-ui/react-icons";
import { CopyIcon } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle
} from "../../../components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from "../../../components/ui/form";
import { Input } from "../../../components/ui/input";
import { LoaderButton } from "../../../components/ui/LoadingSpinner";
import { ScrollArea } from "../../../components/ui/scroll-area";
import { Textarea } from "../../../components/ui/textarea";

const formSchema = z.object({
  deployKey: z.string({
    required_error: "Please enter a Deploy Key",
  }),
  dbtGitRepoUrl: z.string({
    required_error: "Please enter a dbt Git Repo URL",
  }),
  gitRepoType: z.string({
    required_error: "Please enter a git repo type",
  }),
  mainGitBranch: z.string({
    required_error: "Please enter a main git branch",
  }),
  name: z.string({
    required_error: "Please enter a name",
  }),
});

function GithubConnection() {
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [workspace, setWorkspace] = useState<any>();
  const [connectionCheck, setConnectionCheck] = useState<boolean>(false);
  const [tested, setTested] = useState<boolean>(false);
  const router = useRouter();

  // 1. Define your form.
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      deployKey: "",
      dbtGitRepoUrl: "",
      gitRepoType: "",
      mainGitBranch: "",
      name: "",
    },
  });

  // 2. Define a submit handler.
  async function onSubmit(values: z.infer<typeof formSchema>) {
    // Do something with the form values.
    // ✅ This will be type-safe and validated.
    const data = await createGithubConnection({
      deploy_key: values.deployKey,
      dbt_git_repo_url: values.dbtGitRepoUrl,
      git_repo_type: values.gitRepoType,
      main_git_branch: values.mainGitBranch,
      name: values.name,
    });
    setIsSubmitting(true);

    setIsSubmitting(false);
    router.push("/  ");
  }

  async function testConnection() {
    setTested(true);
    const data = await testGitConnection(
      form.getValues().deployKey,
      form.getValues().dbtGitRepoUrl
    );
    if (data.success === true) {
      setConnectionCheck(true);
    } else {
      setConnectionCheck(false);
    }
  }

  useEffect(() => {
    const getSshKeyFunction = async () => {
      const data = await getSshKey(workspace.id);
      if (data) {
        form.setValue('deployKey', data.public_key)
      }
    };

    if (workspace && workspace.id) {
      getSshKeyFunction();
    }
  }, [workspace]);

  useEffect(() => {
    const getWorkspaceFunction = async () => {
      const data = await getWorkspace();
      setWorkspace(data);
    };

    getWorkspaceFunction();
  }, []);

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <Card className="w-full rounded-sm">
          <CardHeader>
            <CardTitle className="text-xl">
              <div className="flex items-center space-x-0">
                <GitHubLogoIcon />
                <div className="pt-0.5 pl-2">Repository</div>
              </div>
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
                      placeholder="dbt Project Path"
                      {...field}
                      defaultValue={field.value}
                      rows={8}
                      disabled={true}
                    />
                  </FormControl>

                  <Button
                    onClick={(event) => {
                      event.preventDefault();
                      navigator.clipboard.writeText(field.value);
                    }}
                    variant="outline"
                    className="float-right"
                  >
                    <CopyIcon />
                  </Button>
                  <FormMessage />
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
                      placeholder="dbtGit Repo URL"
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
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Git Repo Name</FormLabel>
                  <FormControl>
                    <Input placeholder="" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="gitRepoType"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Git Repo Type</FormLabel>
                  <FormControl>
                    <Input placeholder="" {...field} />
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
                    <Input placeholder="" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </CardContent>
          <CardFooter className="flex justify-end">
            <div className="float-right flex ">
              {tested && (
                connectionCheck ? (
                  <div className="text-green-500 mt-2 mr-2">Connection successful</div>
                ) : (
                  <div className="text-red-500  mt-2 mr-2">Connection failed</div>
                ))
              }
              <LoaderButton
                isLoading={isSubmitting}
                isDisabled={isSubmitting}
                type="submit"
                className="mr-2"
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
        <LoaderButton
          isLoading={isSubmitting}
          isDisabled={isSubmitting || !connectionCheck}
          type="submit"
        >
          Add Git Connection
        </LoaderButton>
      </form>
    </Form>
  );
}

export default function AddGithubPage() {
  return (
    <div className="w-full">
      <ScrollArea className="w-full">
        <FullWidthPageLayout title={"Connect"}>
          <GithubConnection />
        </FullWidthPageLayout>
      </ScrollArea>
    </div>
  );
}
