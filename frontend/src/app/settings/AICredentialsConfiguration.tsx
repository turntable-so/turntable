"use client";
import { Alert, AlertTitle } from "@/components/ui/alert";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { zodResolver } from "@hookform/resolvers/zod";
import { Info, WandSparkles } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "../../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import useSession from "../hooks/use-session";

const NoAIProviderFormSchema = z.object({
  aiProvider: z.literal("none"),
});

const OpenAIFormSchema = z.object({
  aiProvider: z.literal("openai"),
  apiKey: z.string().min(1),
});

const AnthropicFormSchema = z.object({
  aiProvider: z.literal("anthropic"),
  apiKey: z.string().min(1),
});

const FormSchema = z.discriminatedUnion("aiProvider", [
  NoAIProviderFormSchema,
  OpenAIFormSchema,
  AnthropicFormSchema,
]);

export default function AICredentialsConfiguration() {
  const { user } = useSession();
  const role = user.workspace_groups.find(
    (workspace: { workspace_id: string }) => workspace.workspace_id === user.current_workspace.id
  )?.name;

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      aiProvider: "none",
    },
  });

  const selectedAIProvider = form.watch("aiProvider");
  function onSubmit(data: z.infer<typeof FormSchema>) {
    console.log(data);
  }

  return (
    <div className="w-full text-black">
      <Card className="w-full rounded-sm">
        <CardHeader>
          <CardTitle className="text-xl">
            <div className="flex items-center">
              <WandSparkles className="mr-2" />
              AI Credentials
            </div>
          </CardTitle>

          <CardDescription>
            When you configure your AI credentials, Turntable will automatically
            generate documentation for your connection&apos;s models and
            columns.
          </CardDescription>
        </CardHeader>
        {role === "Admin" ? (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)}>
              <CardContent className="space-y-4">
                <FormField
                  control={form.control}
                  name="aiProvider"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Provider</FormLabel>
                      <Select
                        onValueChange={(event) => {
                          field.onChange(event);
                          form.clearErrors("apiKey");
                        }}
                        defaultValue={field.value}
                      >
                        <FormControl>
                          <SelectTrigger className="w-full">
                            <SelectValue placeholder="Select a provider" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="none">None</SelectItem>
                          <SelectItem value="openai" caption="gpt-4o">
                            OpenAI
                          </SelectItem>
                          <SelectItem
                            value="anthropic"
                            caption="claude-3-5-sonnet"
                          >
                            Anthropic
                          </SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {selectedAIProvider !== "none" && (
                  <FormField
                    control={form.control}
                    name="apiKey"
                    render={({ field }) => (
                      <FormField
                        control={form.control}
                        name="apiKey"
                        render={() => (
                          <FormItem>
                            <FormLabel>API Key</FormLabel>
                            <FormControl>
                              <Input
                                autoComplete="off"
                                type="password"
                                placeholder={
                                  selectedAIProvider === "openai"
                                    ? "OpenAI Key"
                                    : "Anthropic Key"
                                }
                                {...field}
                              />
                            </FormControl>
                            <FormDescription />
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    )}
                  />
                )}
              </CardContent>
              <CardFooter className="flex justify-end">
                <Button
                  type="submit"
                  disabled={
                    form.formState.isSubmitting ||
                    (form.formState.isDirty && !form.formState.isValid)
                  }
                >
                  Save
                </Button>
              </CardFooter>
            </form>
          </Form>
        ) : (
          <CardContent>
            <Alert className="bg-zinc-100 text-zinc-600">
              <div className="flex align-top gap-1">
                <Info className="h-4 w-4" />
                <AlertTitle>
                  You don&apos;t have permission to edit AI credentials. Contact
                  an administrator for help.
                </AlertTitle>
              </div>
            </Alert>
          </CardContent>
        )}
      </Card>
    </div>
  );
}
