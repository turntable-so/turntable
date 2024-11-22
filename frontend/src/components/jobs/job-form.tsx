import * as React from "react"
import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { ChevronDown, Info } from "lucide-react"
import { useForm } from "react-hook-form"
import { CommandList } from "./command-list"
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { toast } from "sonner"
import { createJob, getEnvironments, updateJob } from "@/app/actions/actions"
import Link from "next/link"

const FormSchema = z.object({
    name: z.string().min(2, {
        message: "Job name can't be empty",
    }),
    dbtresource_id: z.string().min(2, {
        message: "Please select a dbt resource",
    }),
    commands: z.array(z.string()),
    cron_str: z.string()
        .regex(
            /^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])) (\*|([0-9]|1[0-9]|2[0-3])|\*\/([0-9]|1[0-9]|2[0-3])) (\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|1[0-9]|2[0-9]|3[0-1])) (\*|([1-9]|1[0-2])|\*\/([1-9]|1[0-2])) (\*|([0-6])|\*\/([0-6]))$/,
            {
                message: "Invalid cron expression. Format should be like '0 0 * * *' (minute hour day month weekday)",
            }
        )
        .optional(),
});

export default function JobForm({ title, job }: { title: string, job?: any }) {
    const [environments, setEnvironments] = React.useState<[]>([])
    const form = useForm<z.infer<typeof FormSchema>>({
        resolver: zodResolver(FormSchema),
        defaultValues: {
            name: job?.name || "",
            dbtresource_id: job?.dbtresource_id || "",
            commands: Array.isArray(job?.commands) ? job.commands : ["dbt build"],
            cron_str: job?.cron_str || "",
        },
    });
    const router = useRouter()

    useEffect(() => {
        const fetchEnvironments = async () => {
            const environments = await getEnvironments()
            setEnvironments(environments)
        }
        fetchEnvironments()
    }, [])

    async function onSubmit(data: z.infer<typeof FormSchema>) {
        if (job) {
            const result = await updateJob(job.id, data);
            if (result.id) {
                toast.success("Job updated successfully");
                router.push(`/jobs/${result.id}`);
            } else {
                console.error(result)
                toast.error("Failed to update job");
            }
        } else {
            const result = await createJob(data);
            if (result.id) {
                toast.success("Job created successfully");
                router.push(`/jobs/${result.id}`);
            } else {
                console.error(result)
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
                            <CardTitle>Execution Details</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <CommandList form={form} />
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Schedule</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <FormField
                                control={form.control}
                                name="cron_str"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Cron Schedule</FormLabel>
                                        <FormControl>
                                            <Input id="cron-schedule" placeholder="Cron schedule (0 0 * * *)" {...field} />
                                        </FormControl>
                                        <FormDescription>
                                            We recommend using
                                            <Link href="https://crontab.guru/" target="_blank" className="px-1 text-blue-500 underline">
                                                crontab.guru
                                            </Link>
                                            to help create your cron schedule.
                                        </FormDescription>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </CardContent>
                    </Card>
                    <div className="space-x-2 float-right">
                        <Button variant="outline">Cancel</Button>
                        <Button>Save</Button>
                    </div>
                </form>
                <div className='h-48' />
            </Form>
        </div >
    )
}