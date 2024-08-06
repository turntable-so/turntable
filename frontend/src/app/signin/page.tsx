"use client";

import LoginForm from "@/components/auth/login-form";
import { Carter_One } from "next/font/google";

const carterOne = Carter_One(
    { weight: "400", subsets: ["latin"], display: "swap" });

export default function SignInPage() {
    return (
        <div className='h-screen w-full flex justify-center bg-muted items-center mt-[-48px]'>
            <div>
                <div className={`${carterOne.className} text-2xl text-center my-8 py-2`}>
                    turntable
                </div>
                <div className='w-[450px]'>
                    <LoginForm />
                </div>
            </div>
        </div>
    )
}