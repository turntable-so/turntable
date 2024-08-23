"use client";

import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "../../components/ui/card";
import { useThirdPartyProviders } from "../hooks/use-third-party-providers";
import { SymbolIcon } from "@radix-ui/react-icons";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@radix-ui/react-select";

export default function SyncSettings() {
  const { providers } = useThirdPartyProviders();

  return (
    <div className="w-full text-black">
      <Card className="w-full rounded-sm">
        <CardHeader>
          <CardTitle className="text-xl">
            <div className="flex items-center">
              <SymbolIcon className="size-6 mr-2" />
              Sync Settings
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="my-2 grid grid-cols-2 gap-4 items-center">
            <span>Auto-generated descriptions</span>
            <div>
              <Select>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Disabled" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="disabled">Disabled</SelectItem>
                  {providers.map((provider) => (
                    <SelectItem key={provider.type} value={provider.type}>
                      {provider.type}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
