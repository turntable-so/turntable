"use client";

import LoginForm from "@/components/auth/login-form";
import { Card, CardContent, CardTitle } from "@/components/ui/card";
import CreateWorkspaceForm from "@/components/workspaces/create-workspace-form";
import { Carter_One } from "next/font/google";

export default function SignInPage() {
    return (
        <div className='h-screen w-full flex flex-col bg-muted items-center mt-[150px]'>
            <Card className='w-[400px]'>
                <CardTitle className="p-6 text-xl">Create a Workspace</CardTitle>
                <CardContent className='text-xl font-medium my-8'>
                    <CreateWorkspaceForm />
                </CardContent>
            </Card>
        </div>
    )
}