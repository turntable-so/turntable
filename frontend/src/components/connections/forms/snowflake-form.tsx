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
    account: z.string().min(2, {
        message: "Account can't be empty",
    }),
    username: z.string().min(1, {
        message: "Username can't be empty",
    }),
    password: z.string().min(1, {
        message: "Password can't be empty",
    }),
    warehouse: z.string().min(1, {
        message: "Warehouse can't be empty",
    }),
    role: z.string().min(1, {
        message: "Role can't be empty",
    }),
})

export default function SnowflakeForm({ resource, details }: { resource?: any, details?: any }) {
    const router = useRouter()


    const form = useForm<z.infer<typeof FormSchema>>({
        resolver: zodResolver(FormSchema),
        defaultValues: {
            name: resource?.name || "",
            account: details?.account || "",
            username: details?.username || "",
            password: details?.password || "",
            warehouse: details?.warehouse || "",
            role: details?.role || "",
        },
    })



    async function onSubmit(data: z.infer<typeof FormSchema>) {

        const isUpdate = resource?.id

        const payload = {
            resource: {
                name: data.name,
                type: 'db',
            },
            ...(isUpdate ? {} : { subtype: 'snowflake' }),
            config: {
                account: data.account,
                username: data.username,
                password: data.password,
                warehouse: data.warehouse,
                role: data.role,
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

                    <FormField
                        control={form.control}
                        name="account"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Snowflake Account</FormLabel>
                                <FormControl>
                                    <Input placeholder="acme.us-east-1" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <div className='flex space-x-4 w-full'>
                        <div className="w-1/2 pr-2">
                            <FormField
                                control={form.control}
                                name="warehouse"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Default Warehouse</FormLabel>
                                        <FormControl>
                                            <Input placeholder="WAREHOUSE_NAME" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                        <div className="w-1/2 pr-2">
                            <FormField
                                control={form.control}
                                name="role"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Default Role</FormLabel>
                                        <FormControl>
                                            <Input placeholder="SECURITY_ROLE" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                    </div>
                    <div className='flex space-x-4 w-full'>
                        <div className="w-1/2 pr-2">
                            <FormField
                                control={form.control}
                                name="username"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Username</FormLabel>
                                        <FormControl>
                                            <Input placeholder="Username" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                        <div className="w-1/2 pr-2">
                            <FormField
                                control={form.control}
                                name="password"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Password</FormLabel>
                                        <FormControl>
                                            <Input placeholder="Password" {...field} />
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