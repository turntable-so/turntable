"use client";
import { createResource, updateResource } from "@/app/actions/actions";
import { LoaderButton } from "@/components/ui/LoadingSpinner";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
} from "@/components/ui/card";
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
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { Schema, z } from "zod";

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
`;

const FormSchema = z.object({
  name: z.string().min(2, {
    message: "Name can't be empty",
  }),
  service_account: z.string().min(1, {
    message: "Service account can't be empty",
  }),
  should_filter_schema: z.boolean(),
  include_schemas: z.string().optional(),
});

export default function BigqueryForm({
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
      service_account: details?.service_account || "",
      should_filter_schema: details?.schema_include?.length > 0 || false,
      include_schemas: details?.schema_include?.join("\n") || "",
    },
  });

  async function onSubmit(data: z.infer<typeof FormSchema>) {
    let schemas = undefined;
    const isUpdate = resource?.id;

    if (data.should_filter_schema && data.include_schemas) {
      schemas = data.include_schemas
        .split("\n")
        .map((s) => s.trim())
        .filter((s) => s.length > 0);
    }

    const payload = {
      resource: {
        name: data.name,
        type: "db",
      },
      ...(!isUpdate ? { subtype: "bigquery" } : {}),
      config: {
        service_account: data.service_account,
        ...(schemas ? { schema_include: schemas } : {}),
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

  const shouldFilterSchema = form.watch("should_filter_schema");

  type ConnectionCardDefaultProps = {
    variant: "default";
    title: string;
    description?: never;
    children: React.ReactNode;
  };

  type ConnectionCardSideBySideWithDescriptionProps = {
    variant: "sideBySideWithDescription";
    title: string;
    description: string;
    children: React.ReactNode;
  };

  type NewConnectionCardProps =
    | ConnectionCardDefaultProps
    | ConnectionCardSideBySideWithDescriptionProps;

  function NewConnectionCard({
    variant,
    description,
    title,
    children,
  }: NewConnectionCardProps) {
    return (
      <FormItem>
        <Card className="rounded-md">
          <CardHeader>
            <FormLabel>{title}</FormLabel>
          </CardHeader>
          <CardContent
            className={
              variant === "sideBySideWithDescription"
                ? "gap-y-0.5 flex flex-row justify-between"
                : ""
            }
          >
            {variant === "sideBySideWithDescription" && (
              <FormDescription>{description}</FormDescription>
            )}
            <FormControl>{children}</FormControl>
          </CardContent>
          <FormMessage />
        </Card>
      </FormItem>
    );
  }

  return (
    <div className="w-full max-w-2xl">
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="space-y-6 text-black"
        >
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <NewConnectionCard variant="default" title="Connection name">
                <Input placeholder="my awesome connection" {...field} />
              </NewConnectionCard>
            )}
          />
          <FormField
            control={form.control}
            name="service_account"
            render={({ field }) => (
              <NewConnectionCard variant="default" title="Service account">
                <Textarea
                  className="h-[250px]"
                  placeholder={serviceAccountPlaceholder}
                  {...field}
                />
              </NewConnectionCard>
            )}
          />
          <FormField
            control={form.control}
            name="should_filter_schema"
            render={({ field }) => (
              <NewConnectionCard
                variant="sideBySideWithDescription"
                title="Filter schemas (advanced)"
                description={
                  shouldFilterSchema
                    ? "Include only the following schemas:"
                    : "Including all schemas"
                }
              >
                <Switch
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              </NewConnectionCard>
            )}
          />
          {shouldFilterSchema && (
            <FormField
              control={form.control}
              name="include_schemas"
              render={({ field }) => (
                <NewConnectionCard
                  variant="default"
                  title="Add a line for each schema"
                >
                  <Textarea
                    className="h-[150px]"
                    placeholder={"Eg.\nschema1\nschema2"}
                    {...field}
                  />
                </NewConnectionCard>
              )}
            />
          )}
          <div className="flex justify-end pb-4">
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
                onClick={() => testConnection(resource)}
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
