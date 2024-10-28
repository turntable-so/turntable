"use client";

import LoginForm from "@/components/auth/login-form";
import TurntableNamemark from "@/components/logos/turntable-namemark";
import { Carter_One } from "next/font/google";
import { useEffect, useState } from "react";

export default function SignInPage() {
  const [invitationCode, setInvitationCode] = useState<any>(null);
  useEffect(() => {
    if (typeof window !== "undefined") {
      const code = new URLSearchParams(window.location.search).get(
        "invitation_code",
      );
      setInvitationCode(code);
    }
  }, []);
  return (
    <div className="h-screen w-full flex justify-center bg-muted items-center mt-[-48px]">
      <div>
        <div className="mb-12 flex justify-center">
          <TurntableNamemark />
        </div>
        <div className="w-[450px]">
          <LoginForm invitationCode={invitationCode} />
        </div>
      </div>
    </div>
  );
}
