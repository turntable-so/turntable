"use client";
import React from "react";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "../components/ui/command";

import useSession from "@/app/hooks/use-session";
import { Button } from "../components/ui/button";

export default function Home() {
  const session = useSession();

  return <div>{JSON.stringify(session)}</div>;
}
