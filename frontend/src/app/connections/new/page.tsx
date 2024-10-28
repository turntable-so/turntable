"use client";

import BackToConnectionsButton from "@/components/connections/back-to-connections-button";
import {
  BIToolOptions,
  TransformationOptions,
  WarehouseOptions,
} from "@/components/connections/connection-options";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { useRouter } from "next/navigation";

const ConnectionOptionCard = ({
  option,
}: {
  option: {
    label: string;
    logo: React.ReactNode;
    url?: string;
  };
}) => {
  const router = useRouter();

  return (
    <Card
      className={`rounded-lg hover:bg-muted/50 hover:cursor-pointer shadow-none border ${!option.url && "hover:cursor-not-allowed opacity-50"} ${option.url && "hover:border-black"}`}
      onClick={() => {
        if (option.url) {
          router.push(option.url);
        }
      }}
    >
      <CardHeader>
        <div className="flex bg-green-items-center space-x-4 ">
          <div className="h-full w-full flex items-center space-x-4">
            <div>{option.logo}</div>
            <div className="flex w-full items-center justify-between space-x-2">
              <CardTitle>{option.label}</CardTitle>
              {!option.url && <Badge variant="secondary">Coming Soon</Badge>}
            </div>
          </div>
        </div>
      </CardHeader>
    </Card>
  );
};

export default function NewConnectionsPage() {
  return (
    <div className="max-w-7xl w-full px-16 py-4">
      <BackToConnectionsButton />
      <Separator />
      <div>
        <div className="my-8">
          <div className="py-2">Data Warehouses</div>
          <div className="grid grid-cols-2 gap-4">
            {WarehouseOptions.map((option, index) => (
              <ConnectionOptionCard key={index} option={option} />
            ))}
          </div>
        </div>
        <div className="my-8">
          <div className="py-2">Data Transformation</div>
          <div className="grid grid-cols-2 gap-4">
            {TransformationOptions.map((option, index) => (
              <ConnectionOptionCard key={index} option={option} />
            ))}
          </div>
        </div>
        <div className="my-8">
          <div className="py-2">Business Intelligence</div>
          <div className="grid grid-cols-2 gap-4">
            {BIToolOptions.map((option, index) => (
              <ConnectionOptionCard key={index} option={option} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
