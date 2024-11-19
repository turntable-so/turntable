"use client";
import { createResource, updateResource } from "@/app/actions/actions";
import { LoaderButton } from "@/components/ui/LoadingSpinner";
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
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const FormSchema = z.object({
  name: z.string().min(2, {
    message: "Name can't be empty",
  }),
  host: z.string().min(1, {
    message: "Hostname account can't be empty",
  }),
  port: z.coerce.number().min(1, {
    message: "Port can't be empty",
  }),
  database: z.string().min(1, {
    message: "Database can't be empty",
  }),
  username: z.string().min(1, {
    message: "Username can't be empty",
  }),
  password: z.string().min(1, {
    message: "Password can't be empty",
  }),
  serverless: z.boolean().optional(),
});

export default function RedshiftForm({
  resource,
  details,
  testConnection = null,
  tested = false,
  connectionCheck = false,
}: {
  resource?: any;
  details?: any;
  testConnection?: any;
  tested?: boolean;
  connectionCheck?: boolean;
}) {
  const router = useRouter();

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      name: resource?.name || "",
      host: details?.host || "",
      port: details?.port || 5432,
      database: details?.database || "",
      username: details?.username || "",
      password: details?.password || "",
      serverless: details?.serverless || false,
    },
  });

  async function onSubmit(data: z.infer<typeof FormSchema>) {
    const isUpdate = resource?.id;

    const payload = {
      resource: {
        name: data.name,
        type: "db",
      },
      ...(isUpdate ? {} : { subtype: "redshift" }),
      config: {
        host: data.host,
        port: data.port,
        database: data.database,
        username: data.username,
        password: data.password,
        serverless: data.serverless,
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
    <div className="w-full max-w-2xl">
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
                <FormLabel>Connection name</FormLabel>
                <FormControl>
                  <Input placeholder="my awesome connection" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="flex space-x-4 w-full">
            <div className="flex-grow">
              <FormField
                control={form.control}
                name="host"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Hostname</FormLabel>
                    <FormControl>
                      <Input placeholder="host.turntable.so" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="flex-shrink ">
              <FormField
                control={form.control}
                name="port"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Port</FormLabel>
                    <FormControl>
                      <Input type="number" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          </div>
          <FormField
            control={form.control}
            name="database"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Database</FormLabel>
                <FormControl>
                  <Input
                    type="text"
                    placeholder="production_database"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="flex space-x-4 w-full">
            <div className="flex-grow">
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
                      <Input
                        type="password"
                        placeholder="password"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          </div>
          <div>
            <FormField
              control={form.control}
              name="serverless"
              render={({ field }) => (
                <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                  <FormControl>
                    <Checkbox
                      checked={field.value || false}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                  <div className="space-y-1 leading-none">
                    <FormLabel>Is Serverless</FormLabel>
                    <p className="text-sm text-muted-foreground">
                      Whether target Redshift instance is serverless
                      (alternative is provisioned cluster)
                    </p>
                  </div>
                </FormItem>
              )}
            />
          </div>
          <div className="flex justify-end">
            {tested &&
              (connectionCheck ? (
                <div className="text-green-500 mt-2 mr-2">
                  Connection successful
                </div>
              ) : (
                <div className="text-red-500  mt-2 mr-2">Connection failed</div>
              ))}
            {testConnection && (
              <LoaderButton
                className="mr-5"
                onClick={(event) => {
                  event.preventDefault();
                  testConnection(resource);
                }}
              >
                Test
              </LoaderButton>
            )}

            <LoaderButton type="submit">Save</LoaderButton>
          </div>
        </form>
      </Form>
    </div>
  );
}
