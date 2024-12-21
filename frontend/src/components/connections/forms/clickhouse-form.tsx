"use client";
import { createResource, updateResource } from "@/app/actions/actions";
import { LoaderButton } from "@/components/ui/LoadingSpinner";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { PasswordInput } from "@/components/ui/password-input";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const FormSchema = z.object({
    name: z.string().min(2, {
        message: "Connection name can't be empty",
    }),
    host: z.string().min(2, {
        message: "Host can't be empty",
    }),
    port: z.coerce.number().min(1, {
        message: "Port can't be empty",
    }),
    user: z.string().min(1, {
        message: "Username can't be empty",
    }),
    password: z.string().min(1, {
        message: "Password can't be empty",
    }),
    secure: z.boolean().default(false),
});

export default function ClickHouseForm({
    resource,
    details,
}: { resource?: any; details?: any }) {
    const router = useRouter();

    const form = useForm<z.infer<typeof FormSchema>>({
        resolver: zodResolver(FormSchema),
        defaultValues: {
            name: resource?.name || "",
            host: details?.host || "",
            port: details?.port || "",
            user: details?.user || "",
            password: details?.password || "",
            secure: details?.secure || false,
        },
    });

    async function onSubmit(data: z.infer<typeof FormSchema>) {
        const isUpdate = resource?.id;

        const payload = {
            resource: {
                name: data.name,
                type: "db",
            },
            ...(isUpdate ? {} : { subtype: "clickhouse" }),
            config: {
                host: data.host,
                port: data.port,
                user: data.user,
                password: data.password,
                secure: data.secure,
            },
        };
        const res = isUpdate
            ? await updateResource(resource.id, payload)
            : await createResource(payload as any);
        if (res.id) {
            if (isUpdate) {
                toast.success("Connection updated");
            } else {
                toast.success("Connection created");
            }
            router.push(`/connections/${res.id}`);
        } else {
            toast.error("Failed to save connection: " + res[0]);
        }
    }

    return (
        <Card className="w-full max-w-2xl p-6">
            <Form {...form}>
                <form
                    onSubmit={form.handleSubmit(onSubmit)}
                    className="space-y-6 text-black dark:text-white"
                >
                    <FormField
                        control={form.control}
                        name="name"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Connection Name</FormLabel>
                                <FormControl>
                                    <Input placeholder="my ClickHouse connection" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <div className="flex space-x-4 w-full">
                        <div className="w-1/2 pr-2">
                            <FormField
                                control={form.control}
                                name="host"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>ClickHouse Host</FormLabel>
                                        <FormControl>
                                            <Input placeholder="localhost" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                        <div className="w-1/2 pr-2">
                            <FormField
                                control={form.control}
                                name="port"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Port</FormLabel>
                                        <FormControl>
                                            <Input placeholder="8123" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                    </div>
                    <FormField
                        control={form.control}
                        name="user"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Username</FormLabel>
                                <FormControl>
                                    <Input placeholder="default" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="password"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Password</FormLabel>
                                <FormControl>
                                    <PasswordInput  {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="secure"
                        render={({ field }) => (
                            <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md">
                                <FormControl>
                                    <Checkbox
                                        checked={field.value}
                                        onCheckedChange={field.onChange}
                                    />
                                </FormControl>
                                <div className="space-y-1 leading-none">
                                    <FormLabel>Secure Connection</FormLabel>
                                    <p className="text-sm text-muted-foreground">
                                        For secure SSL connection
                                    </p>
                                </div>
                            </FormItem>
                        )}
                    />
                    <div className="flex justify-end">
                        <LoaderButton type="submit">Save</LoaderButton>
                    </div>
                </form>
            </Form>
        </Card>
    );
}