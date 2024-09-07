'use client'
import { createResource, updateResource } from "@/app/actions/actions";
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
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from 'next/navigation';
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
    http_path: z.string().min(2, {
        message: "HTTP Path can't be empty",
    }),
    token: z.string().min(2, {
        message: "Token can't be empty",
    }),
})

export default function DatabricksForm({ resource, details }: { resource?: any, details?: any }) {
    const router = useRouter()


    const form = useForm<z.infer<typeof FormSchema>>({
        resolver: zodResolver(FormSchema),
        defaultValues: {
            name: resource?.name || "",
            host: details?.host || "",
            http_path: details?.http_path || "",
            token: details?.token || "",
        },
    })



    async function onSubmit(data: z.infer<typeof FormSchema>) {

        const isUpdate = resource?.id

        const payload = {
            resource: {
                name: data.name,
                type: 'db',
            },
            ...(isUpdate ? {} : { subtype: 'databricks' }),
            config: {
                host: data.host,
                http_path: data.http_path,
                token: data.token,
            }
        }
        const res = isUpdate ? await updateResource(resource.id, payload) : await createResource(payload as any)
        if (res.id) {
            if (isUpdate) {
                toast.success('Connection updated')
            } else {
                toast.success('Connection created')
            }
            router.push(`/connections/${res.id}`)
        } else {
            toast.error('Failed to save connection: ' + res[0])
        }
    }


    return (
        <div className='w-full max-w-2xl'>
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 text-black">
                    <FormField
                        control={form.control}
                        name="name"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Connection Name</FormLabel>
                                <FormControl>
                                    <Input placeholder="my awesome connection" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <div className='flex space-x-4 w-full'>
                        <div className="w-1/2 pr-2">
                            <FormField
                                control={form.control}
                                name="host"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Databricks Host</FormLabel>
                                        <FormControl>
                                            <Input placeholder="acme.cloud.databricks.com" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                        </div>
                        <div className="w-1/2 pr-2">
                            <FormField
                                control={form.control}
                                name="http_path"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>HTTP Path</FormLabel>
                                        <FormControl>
                                            <Input placeholder="/sql/1.0/warehouses/acme_prod" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                    </div>
                    <div className='flex space-x-4 w-full'>
                        <div className="w-full">
                            <FormField
                                control={form.control}
                                name="token"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Personal Access Token (PAT)</FormLabel>
                                        <FormControl>
                                            <Input placeholder="********" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                    </div>
                    <div className='flex justify-end'>
                        <LoaderButton type='submit'>
                            Save
                        </LoaderButton>
                    </div>
                </form>
            </Form>
        </div >
    )
}