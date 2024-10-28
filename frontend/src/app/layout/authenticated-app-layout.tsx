import useSession from "@/app/hooks/use-session";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import WorkspaceLayout from "./workspace-layout";

export default function AuthenticatedAppLayout({
  children,
}: { children: React.ReactNode }) {
  const session = useSession();
  const router = useRouter();

  useEffect(() => {
    if (session?.user) {
      if (session.user.workspaces.length === 0) {
        router.push("/workspaces");
      }
    }
  }, [session, router]);

  if (
    !session ||
    !session.user ||
    (session.user.workspaces && session.user.workspaces.length === 0)
  ) {
    return null;
  }

  return <WorkspaceLayout>{children}</WorkspaceLayout>;
}
