"use client";

import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "../../components/ui/card";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "../../components/ui/dropdown-menu";
import { MoreHorizontal, Lock, Link2Icon } from "lucide-react";
import { useThirdPartyProviders } from "../hooks/use-third-party-providers";
import { Button } from "../../components/ui/button";
import Link from "next/link";

export default function ThirdPartyCredentials() {
  const { providers } = useThirdPartyProviders();

  return (
    <div className="w-full text-black">
      <Card className="w-full rounded-sm">
        <CardHeader>
          <CardTitle className="text-xl">
            <div className="flex items-center">
              <Link2Icon className="mr-2" />
              Third Party Credentials
            </div>
          </CardTitle>

          <CardDescription>
            Your credentials are encrypted and stored securely
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {providers.map((provider) => (
              <div
                key={provider.type}
                className="py-3 border flex flex-col text-sm px-4 rounded-lg"
              >
                <div className="flex justify-between">
                  <h4 className="text-xl font-semibold">{provider.type}</h4>
                  <div className="self-end">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          className="justify-self-end"
                          aria-haspopup="true"
                          size="icon"
                          variant="ghost"
                        >
                          <MoreHorizontal className="h-4 w-4" />
                          <span className="sr-only">Toggle menu</span>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onClick={() => deleteCredential(provider.type)}
                          className="text-red-500 font-bold cursor-pointer"
                        >
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
                <div className="my-2 grid grid-cols-2 gap-4 items-center">
                  {provider.credentials.map((credential) => (
                    <>
                      <div className="font-semibold">{credential.name}</div>
                      <div className="rounded-lg text-muted-foreground bg-gray-100 p-2 grow">
                        <div className="font-mono text-xs flex items-center ">
                          <Lock className="size-3 mr-2" />
                          Contents are encrypted
                        </div>
                      </div>
                    </>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
        <CardFooter className="flex justify-end">
          <Link href="/settings/add_credential">
            <Button>Add Credential</Button>
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
}
