"use client";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ChevronLeft, Plus } from "lucide-react";
import { useRouter } from "next/navigation";

import {
  PostgresLogo,
  SnowflakeLogo,
} from "@/components/connections/connection-options";
import PostgresForm from "@/components/connections/forms/postgres-form";
import SnowflakeForm from "@/components/connections/forms/snowflake-form";
import { Card } from "@/components/ui/card";

export default function SnowflakePage() {
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
          <SnowflakeLogo />
          <div>Create a Snowflake connection</div>
        </div>
      </Button>
      <Separator />
      <div className="flex justify-center">
        <Card className="flex justify-center w-full py-8">
          <SnowflakeForm />
        </Card>
      </div>
    </div>
  );
}
