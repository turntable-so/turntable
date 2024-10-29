"use client";
import { PlusIcon } from "lucide-react";
import { useRouter } from "next/navigation";
import { Button } from "../ui/button";

export default function NewWorkspaceButton() {
  const router = useRouter();

  return (
    <Button
      variant="secondary"
      className="w-full text-muted-foreground"
      onClick={() => {
        router.push("/workspaces/new");
      }}
    >
      <PlusIcon className="size-4 mr-2" />
      <p className="text-md">Create new workspace</p>
    </Button>
  );
}
