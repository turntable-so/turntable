// @ts-nocheck
"use client";
import React, { useEffect, useRef, useState } from "react";
import { AuthActions } from "@/lib/auth";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { PasswordInput } from "../ui/password-input";
import { LoaderButton } from "../ui/LoadingSpinner";
import { Avatar } from "@radix-ui/react-avatar";
import WorkspaceIcon from "@/components/workspaces/workspace-icon";
import { Upload } from "lucide-react";
import { fetcher } from "@/app/fetcher";
import { useSWRConfig } from "swr";
import useSession from "@/app/hooks/use-session";

const FormSchema = z.object({
  name: z.string().min(2, {
    message: "Name must be at least 2 characters.",
  }),
});

type FormData = {
  name: string;
  iconUrl: string;
};

const UpdateWorkspaceForm = ({ workspace, enabled }: any) => {
  console.log(workspace);
  const router = useRouter();
  const [formRespError, setFormRespError] = useState<string | null>(null);

  const { login, storeToken } = AuthActions();
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const { mutate } = useSWRConfig();

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      name: workspace.name,
    },
  });

  const [iconUrl, setIconUrl] = useState(workspace.icon_url);
  const [iconFile, setIconFile] = useState(null);

  useEffect(() => {
    form.setValue("name", workspace.name);
    setIconUrl(workspace.icon_url);
  }, [workspace]);

  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setIconFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setIconUrl(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUploadClick = (event) => {
    event.preventDefault();
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const onSubmit = async (data: any) => {
    const name = data.name.trim();
    setIsLoading(true);
    setFormRespError(null);
    try {
      const formData = new FormData();
      formData.append("name", name);
      if (iconFile) {
        formData.append("icon_file", iconFile);
      }

      const resp = await fetcher("/workspaces/" + workspace.id + "/", {
        method: "PUT",
        body: formData,
      });
      mutate("/auth/users/me/");
      setIsLoading(false);
    } catch (err: any) {
      setFormRespError(err.json.detail);
    }
  };

  const workspaceName = form.watch("name");
  const { isValid } = form.formState;

  return (
    <div className="space-y-4">
      {formRespError && (
        <CardDescription className=" mb-2 py-2 text-red-500 font-medium">
          {formRespError}
        </CardDescription>
      )}
      <div className="grid gap-8 ">
        <Form {...form}>
          {/* @ts-ignore */}
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <div className="flex items-center space-x-4">
              <WorkspaceIcon
                name={workspaceName || "Personal"}
                iconUrl={iconUrl}
              />
              {enabled && <div className="space-y-2">
                <Label htmlFor="password">Set an Icon</Label>
                <input
                  type="file"
                  accept="image/*"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  style={{ display: "none" }}
                />
                <Button
                  variant="secondary"
                  size="sm"
                  className="flex"
                  onClick={handleUploadClick}
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Image
                </Button>
              </div>}
            </div>
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input disabled={isLoading || !enabled} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {enabled && <LoaderButton
              isLoading={isLoading}
              className="float-right"
              type="submit"
            >
              Save
            </LoaderButton>}
          </form>
        </Form>
      </div>
    </div>
  );
};

export default UpdateWorkspaceForm;
