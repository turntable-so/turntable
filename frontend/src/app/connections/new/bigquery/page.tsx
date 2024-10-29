"use client";
import { BigQueryLogo } from "@/components/connections/connection-options";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ChevronLeft, Plus } from "lucide-react";
import { useRouter } from "next/navigation";

import BigqueryForm from "@/components/connections/forms/bigquery-form";

export default function BigQueryPage() {
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
          <BigQueryLogo />
          <div>Create a BigQuery connection</div>
        </div>
      </Button>
      <Separator />
      <div className="flex justify-center">
        <div className="flex justify-center w-full py-8">
          <BigqueryForm />
        </div>
      </div>
    </div>
  );
}
