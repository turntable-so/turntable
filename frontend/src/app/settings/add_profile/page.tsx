"use client";
import FullWidthPageLayout from "../../../components/layout/FullWidthPageLayout";
import {
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Card,
} from "../../../components/ui/card";
import { Code, ExternalLink, Github, Loader, MoveLeft } from "lucide-react";
import Link from "next/link";
import { unstable_noStore as noStore } from 'next/cache';

import { LoaderButton } from "../../../components/ui/LoadingSpinner";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "../../../components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "../../../components/ui/form";
import { Input } from "../../../components/ui/input";
import { Textarea } from "../../../components/ui/textarea";
import { useState } from "react";
import { createAuthProfile, testConnection } from "../../actions/actions";
import { useRouter } from "next/navigation";
import {
  Select,
  SelectItem,
  SelectTrigger,
  SelectContent,
  SelectValue,
} from "../../../components/ui/select";

const formSchema = z.object({
  name: z.string().min(2, {
    message: "Name must be at least 2 characters.",
  }),
  service: z.enum(["bigquery", "metabase", "tableau", "looker"]),
  account_key: z.string().optional(),
  username: z.string().optional(),
  password: z.string().optional(),
});

function ProfileForm() {
  const router = useRouter();

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [testInProgress, setTestInProgress] = useState<boolean>(false);
  const [testWasSuccessful, setTestWasSuccessful] = useState<boolean | null>(
    null
  );
  const [service, setService] = useState<string>("bigquery");

  // 1. Define your form.
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      service: "bigquery",
    },
  });

  // 2. Define a submit handler.
  async function onSubmit(values: z.infer<typeof formSchema>) {
    // Do something with the form values.
    // ✅ This will be type-safe and validated.
    const { name, service, account_key, username, password } = values;

    setIsLoading(true);
    let data = {
      name,
      description: service + "Profile",
      service_account_key: {},
    };
    if (service === "bigquery") {
      const parsedAccountJson = JSON.parse(account_key as string);
      data = {
        ...data,
        service_account_key: parsedAccountJson,
      };
    } else {
      data = {
        ...data,
        service_account_key: {
          username,
          password,
          method: "password",
        },
      };
    }
    const id = await createAuthProfile(data);
    if (id) {
      router.push(`/settings`);
    } else {
      setIsLoading(false);
    }
  }

  const onTestConnectionClick = async () => {
    setTestInProgress(true);
    const { account_key } = form.getValues();
    const res = await testConnection({
      service_account_key: account_key,
      description: "test",
      name: "test",
    });
    setTestInProgress(false);
    if (res.success === "True") {
      setTestWasSuccessful(true);
    } else {
      setTestWasSuccessful(false);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="service"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Service</FormLabel>
              <FormControl>
                <Select
                  onValueChange={(value) => {
                    setService(value);
                    field.onChange(value);
                  }}
                  defaultValue={service}
                  required
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="bigquery">BigQuery</SelectItem>
                    <SelectItem value="metabase">Metabase</SelectItem>
                    <SelectItem value="tableau">Tableau</SelectItem>
                    <SelectItem value="looker">Looker</SelectItem>
                  </SelectContent>
                </Select>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl>
                <Input placeholder="Metadata Credentials" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        {service === "bigquery" ? (
          <FormField
            control={form.control}
            name="account_key"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Service Account Key</FormLabel>
                <FormControl>
                  <Textarea
                    className="h-48"
                    placeholder="Service Account Key"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        ) : (
          <>
            <FormField
              control={form.control}
              name="username"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    {service === "looker" ? "Client ID" : "Username"}
                  </FormLabel>
                  <FormControl>
                    <Input
                      placeholder={
                        service === "looker" ? "Client ID" : "Username"
                      }
                      {...field}
                    />
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
                  <FormLabel>
                    {service === "looker" ? "Client Secret" : "Password"}
                  </FormLabel>
                  <FormControl>
                    <Input
                      placeholder={
                        service === "looker" ? "Client ID" : "Username"
                      }
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </>
        )}
        <div className="p-0">
          {testWasSuccessful !== null &&
            service === "bigquery" &&
            (testWasSuccessful ? (
              <FormMessage className="text-green-500">
                Connection successful
              </FormMessage>
            ) : (
              <FormMessage className="">Connection failed</FormMessage>
            ))}

          {service === "bigquery" && (
            <LoaderButton
              isLoading={testInProgress}
              isDisabled={testInProgress}
              onClick={onTestConnectionClick}
              type="button"
              variant="secondary"
            >
              Test Connection
            </LoaderButton>
          )}
        </div>
        <div className="flex justify-end space-x-4">
          <LoaderButton
            isLoading={isLoading}
            isDisabled={isLoading}
            type="submit"
          >
            Save
          </LoaderButton>
        </div>
      </form>
    </Form>
  );
}

export default function AddBigQueryProfile() {
  noStore()

  return (
    <FullWidthPageLayout title="Add a Secret">
      <Link
        href="/settings"
        className="text-black opacity-50 flex cursor-pointer hover:opacity-100"
      >
        <MoveLeft className="mr-2" />
        <div>Back to Settings</div>
      </Link>
      <Card className="w-full rounded-sm mt-8">
        <CardHeader>
          <CardTitle className="text-xl">
            <div className="flex items-center">Add Service Account</div>
          </CardTitle>
          <CardDescription>
            Your credential details are encrypted. You wont be able to view or
            change after saving.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ProfileForm />
        </CardContent>
      </Card>
    </FullWidthPageLayout>
  );
}
