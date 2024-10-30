"use client";

import React from "react";

import useSession from "@/app/hooks/use-session";

export default function Home() {
  const session = useSession();

  return <div>{JSON.stringify(session)}</div>;
}
