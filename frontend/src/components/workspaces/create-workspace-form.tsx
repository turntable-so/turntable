// @ts-nocheck
"use client"
import { AuthActions } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import {
    CardDescription
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";


import { createWorkspace } from "@/app/actions/actions";
import useSession from "@/app/hooks/use-session";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from "@/components/ui/form";
import WorkspaceIcon from "@/components/workspaces/workspace-icon";
import { zodResolver } from "@hookform/resolvers/zod";
import { Upload } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { LoaderButton } from "../ui/LoadingSpinner";

const FormSchema = z.object({
    name: z.string().min(2, {
        message: "Name must be at least 2 characters.",
    }),
})



type FormData = {
    name: string;
    iconUrl: string;
};

const CreateWorkspaceForm = () => {
    const {
        register,
        handleSubmit,
        formState: { errors },
        setError,
    } = useForm<FormData>();
    const [iconUrl, setIconUrl] = useState(null);
    const [iconFile, setIconFile] = useState(null);

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

    const { mutate } = useSession()

    const router = useRouter();

    const [formRespError, setFormRespError] = useState<string | null>(null)

    const { login, storeToken } = AuthActions();
    const [isLoading, setIsLoading] = useState<boolean>(false)


    const form = useForm<z.infer<typeof FormSchema>>({
        resolver: zodResolver(FormSchema),
        defaultValues: {
            name: "",
        },
    })

    const onSubmit = async (data: FormData) => {
        const name = data.name.trim()

        setIsLoading(true)
        setFormRespError(null)
        const formData = new FormData();
        formData.append("name", name);
        if (iconFile) {
            formData.append("icon_file", iconFile);
        }
        const workspace = await createWorkspace(formData)
        if (workspace.id) {
            await mutate()
            router.push("/connections")
        }
    };

    const workspaceName = form.watch('name')
    const { isValid } = form.formState

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
                            <WorkspaceIcon name={workspaceName || 'Personal'} iconUrl={iconUrl || ""} />
                            <div className='space-y-2'>
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
                            </div>
                        </div>
                        <FormField
                            control={form.control}
                            name="name"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Name</FormLabel>
                                    <FormControl>
                                        <Input disabled={isLoading} {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <LoaderButton isLoading={isLoading} isDisabled={!isValid} className='float-right'>Save</LoaderButton>
                    </form>
                </Form>
            </div>
        </div >
    );
};

export default CreateWorkspaceForm;
