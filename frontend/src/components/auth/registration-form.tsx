"use client"
import React, { useState } from "react";
import { AuthActions } from "@/lib/auth";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"


import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { PasswordInput } from "../ui/password-input";
import { LoaderButton } from "../ui/LoadingSpinner";
import {
    setCookie,
  } from "cookies-next";
const FormSchema = z.object({
    email: z.string().email('Invalid email address'),
    password: z.string().min(8, {
        message: "Password must be at least 8 characters.",
    }),

})



type FormData = {
    email: string;
    password: string;
};

const RegistrationForm = ({invitationCode = ''} : any) => {
    const router = useRouter();

    const [formRespError, setFormRespError] = useState<string | null>(null)

    const { login, storeToken } = AuthActions();
    const [isLoading, setIsLoading] = useState<boolean>(false)
    const { register: registerUser } = AuthActions(); // Note: Renamed to avoid naming conflict with useForm's register

    const form = useForm<z.infer<typeof FormSchema>>({
        resolver: zodResolver(FormSchema),
        defaultValues: {
            email: "",
            password: "",
        },
    })
    const { setError, formState: { errors } } = form

    const onSubmit = (data: FormData) => {
        setIsLoading(true)
        setFormRespError(null)

        registerUser(data.email, data.password, invitationCode)
            .json((answer) => {
                console.log(answer)
                setCookie("accessToken", answer.tokens.access);
                setCookie("refreshToken", answer.tokens.refresh);
                router.push("/"); // Adjust the path as needed
            })
            .catch((err) => {
                console.log("ERROR")
                console.log(err)
                if (err?.json?.email) {
                    setError("email", { type: "server", message: err.json.email })
                }
                if (err?.json?.password) {
                    setError("password", { type: "server", message: err.json.password })
                }
                if (err instanceof TypeError && err.message === "Failed to fetch") {
                    setFormRespError("Unable to connect to the server. Please try again.")
                }
                setIsLoading(false)
            });
    };

    return (
        <Card className="mx-auto max-w-sm py-4">
            <CardHeader>
                <CardTitle className="text-xl text-center">Get started</CardTitle>
            </CardHeader>
            <CardContent>
                {formRespError && (
                    <CardDescription className=" mb-2 py-2 text-red-500 font-medium">
                        {formRespError}
                    </CardDescription>
                )}
                <div className="grid gap-4">
                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                            <FormField
                                control={form.control}
                                name="email"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Email</FormLabel>
                                        <FormControl>
                                            <Input disabled={isLoading} placeholder="email@yourcompany.com" {...field} />
                                        </FormControl>
                                        <FormMessage>
                                            {errors?.email?.message}
                                        </FormMessage>
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="password"

                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>
                                            <div className="flex items-center">
                                                <Label htmlFor="password">Password</Label>
                                            </div>
                                        </FormLabel>
                                        <FormControl>
                                            <PasswordInput disabled={isLoading} {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <LoaderButton isLoading={isLoading} className='w-full' type="submit">Continue</LoaderButton>
                        </form>
                    </Form>
                </div>
                <div className="mt-4 text-center text-sm">
                    Already have an account?{" "}
                    <Link href='/signin' className="underline">
                        Log in
                    </Link>
                </div>
            </CardContent>
        </Card>
    );
};

export default RegistrationForm;
