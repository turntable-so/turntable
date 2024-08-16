"use client";

import RegistrationForm from "@/components/auth/registration-form";
import { Carter_One } from "next/font/google";
import { useState, useEffect } from "react";

const carterOne = Carter_One(
    { weight: "400", subsets: ["latin"], display: "swap" });

export default function SignInPage() {
    const [invitationCode, setInvitationCode] = useState<any>(null);
    useEffect(() => {
        if (typeof window !== "undefined") {
            const code = new URLSearchParams(window.location.search).get('invitation_code');
            setInvitationCode(code);
        }
    }, []);
    return (
        <div className='h-screen w-full flex justify-center bg-muted items-center mt-[-48px]'>
            <div>
                <div className={`${carterOne.className} text-2xl text-center my-8 py-2`}>
                    turntable
                </div>
                <div className='w-[450px]'>
                    <RegistrationForm invitationCode={invitationCode} />
                </div>
            </div>
        </div>
    )
}