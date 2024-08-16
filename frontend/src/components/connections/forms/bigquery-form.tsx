'use client'
import { createResource, updateResource } from "@/app/actions/actions";
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
import { LoaderButton } from "@/components/ui/LoadingSpinner";
import { Switch } from '@/components/ui/switch';
import { Textarea } from "@/components/ui/textarea";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from 'next/navigation';
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const serviceAccountPlaceholder = `{
  "type": "service_account",
  "project_id": "...",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "...",
  "token_uri": "...",
  "auth_provider_x509_cert_url": "...",,
  "client_x509_cert_url": "...",
  "universe_domain": "..."
}
`

const FormSchema = z.object({
    name: z.string().min(2, {
        message: "Name can't be empty",
    }),
    service_account: z.string().min(1, {
        message: "Service account can't be empty",
    }),
    should_filter_schema: z.boolean(),
    include_schemas: z.string().optional(),
})

export default function BigqueryForm({ resource, details }: { resource?: any, details?: any }) {
    const router = useRouter()


    console.log({ resource, details })
    const form = useForm<z.infer<typeof FormSchema>>({
        resolver: zodResolver(FormSchema),
        defaultValues: {
            name: resource?.name || "",
            service_account: details?.service_account || "",
            should_filter_schema: details?.schema_include?.length > 0 || false,
            include_schemas: details?.schema_include?.join('\n') || '',
        },
    })



    async function onSubmit(data: z.infer<typeof FormSchema>) {
        let schemas = undefined
        const isUpdate = resource?.id

        if (data.should_filter_schema && data.include_schemas) {
            schemas = data.include_schemas
                .split('\n')
                .map((s) => s.trim())
                .filter((s) => s.length > 0)
        }

        const payload = {
            resource: {
                name: data.name,
                type: 'db',
            },
            ...(!isUpdate ? { subtype: 'bigquery' } : {}),
            config: {
                service_account: data.service_account,
                ...(schemas ? { schema_include: schemas } : {}),
            }
        }
        const res = isUpdate ? await updateResource(resource.id, payload) : await createResource(payload as any)
        console.log({ res })
        if (!res.id) {
            toast.error('Failed to save connection: ' + res[0])
        }
        if (res.id && resource?.id) {
            toast.success('Connection updated')
            router.push(`/connections/${resource.id}`)
        }
        else if (res.id) {
            router.push(`/connections/`)
        }
    }

    const shouldFilterSchema = form.watch('should_filter_schema')

    return (
        <div className='w-full max-w-2xl'>
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 text-black">
                    <FormField
                        control={form.control}
                        name="name"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Connection name</FormLabel>
                                <FormControl>
                                    <Input placeholder="my awesome connection" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="service_account"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Service account</FormLabel>
                                <FormControl>
                                    <Textarea className='h-[250px]' placeholder={serviceAccountPlaceholder} {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <div className='space-y-2'>
                        <FormField
                            control={form.control}
                            name="should_filter_schema"
                            render={({ field }) => (
                                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm">
                                    <div className="space-y-0.5">
                                        <FormLabel>Filter schemas (advanced)</FormLabel>
                                        <FormDescription>
                                            {shouldFilterSchema ? 'Include only the following schemas:' : 'Including all schemas'}
                                        </FormDescription>
                                    </div>
                                    <FormControl>
                                        <Switch
                                            checked={field.value}
                                            onCheckedChange={field.onChange}
                                        />
                                    </FormControl>
                                </FormItem>
                            )}
                        />
                        {shouldFilterSchema && (
                            <FormField
                                control={form.control}
                                name="include_schemas"
                                render={({ field }) => (
                                    <FormItem className='bg-muted p-4'>
                                        <div className='text-xs text-muted-foreground font-medium'>Add a line for each schema</div>
                                        <FormControl>
                                            <Textarea className='h-[150px]' placeholder={'Eg.\nschema1\nschema2'} {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        )}
                    </div>

                    <div className='flex justify-end'>
                        <LoaderButton type='submit'>
                            Save
                        </LoaderButton>
                    </div>
                </form>
            </Form>
        </div>
    )
}