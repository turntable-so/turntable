"use client";
import { AuthActions } from "@/lib/auth";
import { SignInResponse, signIn } from "next-auth/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { zodResolver } from "@hookform/resolvers/zod";
import { setCookie } from "cookies-next";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { LoaderButton } from "../ui/LoadingSpinner";
import { PasswordInput } from "../ui/password-input";
const FormSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, {
    message: "Password must be at least 8 characters.",
  }),
});

type FormData = {
  email: string;
  password: string;
};

const GoogleLogo = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="0.98em"
    height="1em"
    viewBox="0 0 256 262"
  >
    <path
      fill="#4285f4"
      d="M255.878 133.451c0-10.734-.871-18.567-2.756-26.69H130.55v48.448h71.947c-1.45 12.04-9.283 30.172-26.69 42.356l-.244 1.622l38.755 30.023l2.685.268c24.659-22.774 38.875-56.282 38.875-96.027"
    />
    <path
      fill="#34a853"
      d="M130.55 261.1c35.248 0 64.839-11.605 86.453-31.622l-41.196-31.913c-11.024 7.688-25.82 13.055-45.257 13.055c-34.523 0-63.824-22.773-74.269-54.25l-1.531.13l-40.298 31.187l-.527 1.465C35.393 231.798 79.49 261.1 130.55 261.1"
    />
    <path
      fill="#fbbc05"
      d="M56.281 156.37c-2.756-8.123-4.351-16.827-4.351-25.82c0-8.994 1.595-17.697 4.206-25.82l-.073-1.73L15.26 71.312l-1.335.635C5.077 89.644 0 109.517 0 130.55s5.077 40.905 13.925 58.602z"
    />
    <path
      fill="#eb4335"
      d="M130.55 50.479c24.514 0 41.05 10.589 50.479 19.438l36.844-35.974C195.245 12.91 165.798 0 130.55 0C79.49 0 35.393 29.301 13.925 71.947l42.211 32.783c10.59-31.477 39.891-54.251 74.414-54.251"
    />
  </svg>
);

const LoginForm = ({ invitationCode = "" }: any) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm<FormData>();

  const router = useRouter();

  const [formRespError, setFormRespError] = useState<string | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(false);

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: FormData) => {
    setIsLoading(true);
    setFormRespError(null);
    const res = await signIn("credentials", {
      email: data.email,
      password: data.password,
      redirect: false,
    });
    if (res?.status === 401) {
      setFormRespError(res?.error || "");
    } else {
      router.replace("/");
    }
    setIsLoading(false);
  };

  return (
    <Card className="mx-auto max-w-sm py-4">
      <CardHeader>
        <CardTitle className="text-xl text-center">Log in</CardTitle>
      </CardHeader>
      <CardContent>
        {formRespError && (
          <CardDescription className="mb-2 py-2 text-red-500 font-medium">
            {formRespError}
          </CardDescription>
        )}
        <div className="grid gap-4">
          <div className="flex flex-col items-center mt-4">
            <Button
              variant="ghost"
              className="border-black border w-full"
              onClick={() => {
                setCookie("invitationCode", invitationCode);
                signIn("google");
              }}
            >
              <div className="mr-2">
                <GoogleLogo />
              </div>
              Continue with Google
            </Button>
          </div>
          <div className="text-muted-foreground text-sm text-center my-2"></div>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input
                        disabled={isLoading}
                        placeholder="email@yourcompany.com"
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
                      <div className="flex items-center">
                        <Label htmlFor="password">Password</Label>
                        <Link
                          href="#"
                          className="ml-auto inline-block text-sm underline"
                        >
                          Forgot your password?
                        </Link>
                      </div>
                    </FormLabel>
                    <FormControl>
                      <PasswordInput disabled={isLoading} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <LoaderButton
                isLoading={isLoading}
                className="w-full"
                type="submit"
              >
                Log in
              </LoaderButton>
            </form>
          </Form>
          <div className="my-2 text-center text-sm">
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="underline">
              Sign up
            </Link>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default LoginForm;
