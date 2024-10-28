"use client";
import { createResource, updateResource } from "@/app/actions/actions";
import { LoaderButton } from "@/components/ui/LoadingSpinner";
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
  client_id: z.string().min(1, {
    message: "Client ID can't be empty",
  }),
  client_secret: z.string().min(1, {
    message: "Client secret can't be empty",
  }),
  powerbi_workspace_id: z.string().min(1, {
    message: "Workspace ID can't be empty",
  }),
  powerbi_tenant_id: z.string().min(1, {
    message: "Tenant ID can't be empty",
  }),
});

export default function PowerBIForm({
  resource,
  details,
}: { resource?: any; details?: any }) {
  const router = useRouter();

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      name: resource?.name || "",
      client_id: details?.client_id || "",
      client_secret: details?.client_secret || "",
      powerbi_workspace_id: details?.powerbi_workspace_id || "",
      powerbi_tenant_id: details?.powerbi_tenant_id || "",
    },
  });

  async function onSubmit(data: z.infer<typeof FormSchema>) {
    const isUpdate = resource?.id;

    const payload = {
      resource: {
        name: data.name,
        type: "bi",
      },
      ...(isUpdate ? {} : { subtype: "powerbi" }),
      config: {
        client_id: data.client_id,
        client_secret: data.client_secret,
        powerbi_workspace_id: data.powerbi_workspace_id,
        powerbi_tenant_id: data.powerbi_tenant_id,
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
      toast.error(`Failed to save connection: ${res[0]}`);
    }
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
              <FormItem>
                <FormLabel>Connection name</FormLabel>
                <FormControl>
                  <Input placeholder="My PowerBI connection" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="client_id"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Client ID</FormLabel>
                <FormControl>
                  <Input placeholder="Client ID" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="client_secret"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Client Secret</FormLabel>
                <FormControl>
                  <Input placeholder="Client Secret" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="powerbi_workspace_id"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Workspace ID</FormLabel>
                <FormControl>
                  <Input placeholder="Workspace ID" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="powerbi_tenant_id"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Tenant ID</FormLabel>
                <FormControl>
                  <Input placeholder="Tenant ID" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="flex justify-end">
            <LoaderButton type="submit">Save</LoaderButton>
          </div>
        </form>
      </Form>
    </div>
  );
}
