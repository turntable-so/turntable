import { createJob, getEnvironments, updateJob } from "@/app/actions/actions";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Form,
  FormControl,
  FormDescription,
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
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { CommandList } from "./command-list";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PasswordInput } from "../ui/password-input";
import { buildWebhookUrl } from "@/lib/webhooks";

const FormSchema = z.object({
  name: z.string().min(2, {
    message: "Job name can't be empty",
  }),
  dbtresource_id: z.string().min(2, {
    message: "Please select a dbt resource",
  }),
  commands: z.array(z.string()),
  workflow_type: z.enum(['cron', 'webhook']).default('cron'),
  cron_str: z.string()
    .transform((str) => (str === undefined ? str : str.trim()))
    .optional(),
  save_artifacts: z.boolean().default(true),
  hmac_secret_key: z.string().optional(),
}).superRefine((data, ctx) => {
  if (data.workflow_type === 'cron' && !data.cron_str) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "Cron schedule is required for scheduled jobs",
      path: ["cron_str"],
    });
  }

  if (data.workflow_type === 'webhook' && !data.hmac_secret_key) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "Webhook secret is required for webhook jobs",
      path: ["hmac_secret_key"],
    });
  }

  if (data.workflow_type === 'cron' && data.cron_str) {
    const cronRegex = /^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])) (\*|([0-9]|1[0-9]|2[0-3])|\*\/([0-9]|1[0-9]|2[0-3])) (\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|1[0-9]|2[0-9]|3[0-1])) (\*|([1-9]|1[0-2])|\*\/([1-9]|1[0-2])) (\*|([0-6])|\*\/([0-6]))$/;
    if (!cronRegex.test(data.cron_str)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Invalid cron expression. Format should be like '0 0 * * *' (minute hour day month weekday)",
        path: ["cron_str"],
      });
    }
  }
});

export default function JobForm({ title, job }: { title: string; job?: any }) {
  const [environments, setEnvironments] = React.useState<[]>([]);
  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      name: job?.name || "",
      dbtresource_id: job?.dbtresource_id || "",
      commands: Array.isArray(job?.commands) ? job.commands : ["dbt build"],
      cron_str: job?.cron_str || "",
      save_artifacts:
        job?.save_artifacts !== undefined ? job.save_artifacts : true,
      hmac_secret_key: job?.hmac_secret_key || "",
      workflow_type: job?.workflow_type || "cron",
    },
  });
  const router = useRouter();

  useEffect(() => {
    const fetchEnvironments = async () => {
      const environments = await getEnvironments();
      setEnvironments(environments);
    };
    fetchEnvironments();
  }, []);

  async function onSubmit(data: z.infer<typeof FormSchema>) {
    if (data.workflow_type === 'webhook') {
      delete data.cron_str;
    }
    if (job) {
      const result = await updateJob(job.id, data);
      if (result.id) {
        toast.success("Job updated successfully");
        router.push(`/jobs/${result.id}`);
      } else {
        console.error(result);
        toast.error("Failed to update job");
      }
    } else {
      const result = await createJob(data);
      if (result.id) {
        toast.success("Job created successfully");
        router.push(`/jobs/${result.id}`);
      } else {
        console.error(result);
        toast.error("Failed to create job");
      }
    }
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-medium">{title}</h1>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Job Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Job name</FormLabel>
                    <FormControl>
                      <Input placeholder="New job" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="dbtresource_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Environment</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select..." />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {environments.map((env: any) => (
                          <SelectItem key={env.id} value={env.id}>
                            {env.environment}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Trigger</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs
                defaultValue="schedule"
                className="w-full"
                onValueChange={(value) => {
                  form.setValue('workflow_type', value === 'schedule' ? 'cron' : 'webhook');
                }}
              >
                <TabsList className="">
                  <TabsTrigger value="schedule">Schedule</TabsTrigger>
                  <TabsTrigger value="webhook">Webhook</TabsTrigger>
                </TabsList>
                <TabsContent value="schedule" className="space-y-4">
                  <FormField
                    control={form.control}
                    name="cron_str"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Cron Schedule</FormLabel>
                        <FormControl>
                          <Input
                            id="cron-schedule"
                            placeholder="Cron schedule (0 0 * * *)"
                            {...field}
                          />
                        </FormControl>
                        <FormDescription>
                          We recommend using
                          <Link
                            href="https://crontab.guru/"
                            target="_blank"
                            className="px-1 text-blue-500 underline"
                          >
                            crontab.guru
                          </Link>
                          to help create your cron schedule.
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </TabsContent>
                <TabsContent value="webhook" className="space-y-4">
                  <FormLabel className="my-2"  >
                    <p>Webhook Trigger URL</p>

                    <a href={buildWebhookUrl(job?.id)} className="text-blue-500 underline">{buildWebhookUrl(job?.id)}</a>
                  </FormLabel>
                  <FormField
                    control={form.control}
                    name="hmac_secret_key"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Webhook Secret</FormLabel>
                        <FormControl>
                          <PasswordInput
                            placeholder="Enter secret key"
                            value={field.value || ''}
                            onChange={field.onChange}
                          />
                        </FormControl>
                        <FormDescription>
                          This secret key will be required to authenticate webhook requests using <a href="https://dev.to/prismatic/how-to-secure-webhook-endpoints-with-hmac-39cb" target="_blank" className="text-blue-500 underline">HMAC</a>
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Execution Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-8">
              <CommandList form={form} />

              <div className="flex flex-col gap-4">
                <h3 className="font-semibold leading-none tracking-tight">Options</h3>
                <FormField
                  control={form.control}
                  name="save_artifacts"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center space-x-2">
                      <FormControl>
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={(checked) => field.onChange(checked)}
                        />
                      </FormControl>
                      <FormLabel className="font-normal cursor-pointer" style={{ margin: "0 0 0 8px" }}>Save Artifacts</FormLabel>
                    </FormItem>
                  )}
                />
              </div>
            </CardContent>
          </Card>


          <div className="space-x-2 float-right">
            <Button variant="outline">Cancel</Button>
            <Button>Save</Button>
          </div>
        </form>
        <div className="h-48" />
      </Form>
    </div>
  );
}
