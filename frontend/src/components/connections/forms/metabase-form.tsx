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
        message: "Name can't be empty",
    }),
    connect_uri: z.string().min(1, {
        message: "Metabase uri can't be empty",
    }),
    username: z.string().min(1, {
        message: "Username can't be empty",
    }),
    password: z.string().min(1, {
        message: "Password can't be empty",
    }),
})

export default function MetabaseForm({ resource, details }: { resource?: any, details?: any }) {
    const router = useRouter()


    console.log({ resource, details })
    const form = useForm<z.infer<typeof FormSchema>>({
        resolver: zodResolver(FormSchema),
        defaultValues: {
            name: resource?.name || "",
            connect_uri: details?.connect_uri || "",
            username: details?.username || "",
            password: details?.password || "",
        },
    })



    async function onSubmit(data: z.infer<typeof FormSchema>) {
        const isUpdate = resource?.id

        const payload = {
            resource: {
                name: data.name,
                type: 'db',
            },
            ...(isUpdate ? {} : { subtype: 'metabase' }),
            config: {
                connect_uri: data.connect_uri,
                username: data.username,
                password: data.password,
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
                    <div className='flex space-x-4 w-full'>
                        <div className='flex-grow'>
                            <FormField
                                control={form.control}
                                name="connect_uri"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Metabase URI</FormLabel>
                                        <FormControl>
                                            <Input placeholder="http://metabase:4000" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                    </div>

                    <div className='flex space-x-4 w-full'>
                        <div className='flex-grow'>
                            <FormField
                                control={form.control}
                                name="username"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Username</FormLabel>
                                        <FormControl>
                                            <Input placeholder="username" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                        <div className="flex-grow">
                            <FormField
                                control={form.control}
                                name="password"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Password</FormLabel>
                                        <FormControl>
                                            <Input type='password' placeholder="password" {...field} />
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