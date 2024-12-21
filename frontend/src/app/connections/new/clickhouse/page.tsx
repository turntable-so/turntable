"use client";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ChevronLeft, Plus } from "lucide-react";
import { useRouter } from "next/navigation";

import {
    ClickhouseLogo,
} from "@/components/connections/connection-options";
import ClickhouseForm from "@/components/connections/forms/clickhouse-form";

export default function ClickhousePage() {
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
                    <ClickhouseLogo width={24} height={24} />
                    <div>Create a Clickhouse connection</div>
                </div>
            </Button>
            <Separator />
            <div className="flex justify-center">
                <div className="flex justify-center w-full py-8">
                    <ClickhouseForm />
                </div>
            </div>
        </div>
    );
}
