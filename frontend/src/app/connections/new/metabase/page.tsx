"use client";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ChevronLeft } from "lucide-react";
import { useRouter } from "next/navigation";

import MetabaseForm from "@/components/connections/forms/metabase-form";
import { MetabaseIcon } from "@/lib/utils";

export default function MetabasePage() {
  const router = useRouter();

  return (
    <div className="max-w-7xl w-full px-16 py-4">
      <Button
        variant="ghost"
        className="my-4 text-lg  flex items-center space-x-4"
        onClick={() => {
          router.push("/connections/new");
        }}
      >
        <ChevronLeft className="size-5" />
        <div className="flex items-center space-x-2">
          <MetabaseIcon />
          <div>Create a Metabase connection</div>
        </div>
      </Button>
      <Separator />
      <div className="flex justify-center">
        <div className="flex justify-center w-full py-8">
          <MetabaseForm />
        </div>
      </div>
    </div>
  );
}
