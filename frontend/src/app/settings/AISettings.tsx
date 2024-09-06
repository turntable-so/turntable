"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { DropdownMenu } from "@/components/ui/dropdown-menu";
import { Plus } from "lucide-react";
import useSession from "../hooks/use-session";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { LoaderButton } from "@/components/ui/LoadingSpinner";
import { toast } from "sonner";
import {
  createWorkspaceSettings,
  setWorkspaceSettings,
} from "../actions/actions";

export default function AISettings({ workspaceSettings }) {
  const { user } = useSession();
  if (!isUserAdmin(user)) {
    return <></>;
  }
  const providers = ["OpenAI", "Anthropic"];

  let settingsMap = {};
  for (const setting of workspaceSettings) {
    settingsMap[setting.name] = setting;
  }

  console.log(settingsMap);

  const FormSchema = z.object({
    aiProvider: z.string().min(1, {
      message: "AI Provider can't be empty",
    }),
    openAiApiKey: z.string(),
    anthropicApiKey: z.string(),
  });

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      aiProvider: settingsMap.aiProvider?.plaintext_value || "anthropic",
      // we will never get the key back from the server
      openAiApiKey: "",
      anthropicApiKey: "",
    },
  });

  async function onSubmit(
    data: z.infer<typeof FormSchema> | z.infer<typeof FormSchema>
  ) {
    const { aiProvider, openAiApiKey, anthropicApiKey } = data;
    if (!isUserAdmin(user)) {
      toast.error("Only Admins can edit these settings");
      return;
    }
    createOrUpdateSetting(
      "aiProvider",
      settingsMap,
      user.current_workspace,
      aiProvider
    );
    createOrUpdateSetting(
      "openAiApiKey",
      settingsMap,
      user.current_workspace,
      openAiApiKey,
      true
    );
    createOrUpdateSetting(
      "anthropicApiKey",
      settingsMap,
      user.current_workspace,
      anthropicApiKey,
      true
    );
    toast.success("AI settings updated");
    // const res = isUpdate
    //   ? await updateResource(resource.id, payload)
    //   : await createResource(payload as any);
    // if (res.id) {
    //   toast.success("AI settings updated");
    // } else {
    //   toast.error("Failed to save settings: " + res[0]);
    // }
  }

  return (
    <div className="w-full text-black">
      <Card className="w-full rounded-sm">
        <CardHeader>
          <CardTitle className="text-xl">
            <div className="flex items-center">
              <Plus className="mr-2" />
              AI Settings
            </div>
          </CardTitle>
          <CardDescription>
            Choose your preferred AI provider and set your API keys
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form
              onSubmit={form.handleSubmit(onSubmit)}
              className="space-y-6 text-black"
            >
              <FormField
                control={form.control}
                name="aiProvider"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>AI Provider</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select an AI Provider" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {providers.map((provider: string) => (
                          <SelectItem
                            key={provider.toLowerCase()}
                            value={provider.toLowerCase()}
                          >
                            {provider}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="openAiApiKey"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>OpenAI API key</FormLabel>
                    <FormControl>
                      <Input placeholder="******" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="anthropicApiKey"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Anthropic API key</FormLabel>
                    <FormControl>
                      <Input placeholder="******" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex justify-end">
                <LoaderButton type="submit">Save AI Settings</LoaderButton>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}

function isUserAdmin(user: any): Boolean {
  const currentWorkspace = user.current_workspace;
  for (let workspace_group of user.workspace_groups) {
    if (workspace_group.workspace_id === currentWorkspace.id)
      return workspace_group.name === "Admin";
  }
  return false;
}

function createOrUpdateSetting(
  name: string,
  settingsMap: any,
  workspace: any,
  value: string,
  secret = false
) {
  let body = {
    name: name,
    workspace: workspace.id,
    secret_value: secret ? value : null,
    plaintext_value: secret ? null : value,
  };

  if (name in settingsMap) {
    if (!isSettingSame(settingsMap[name], body)) {
      setWorkspaceSettings(settingsMap[name].id, body);
    }
  } else {
    createWorkspaceSettings(name, body);
  }
}

function isSettingSame(setting: any, setting2: any) {
  if (setting.secret_value !== setting2.secret_value) return false;
  if (setting.plaintext_value !== setting2.plaintext_value) return false;
  if (setting.name !== setting2.name) return false;
}
