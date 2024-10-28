"use client";

import RegistrationForm from "@/components/auth/registration-form";
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
        <div className="flex justify-center mb-10">
          <div>
            <div className="mb-12 flex justify-center">
              <TurntableNamemark />
            </div>
            <div className="w-[450px]">
              <RegistrationForm invitationCode={invitationCode} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
