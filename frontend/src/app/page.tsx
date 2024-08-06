'use client'
import { CommandDialog, CommandInput, CommandList, CommandEmpty, CommandGroup, CommandItem } from "../components/ui/command"
import React from "react"


import { Button } from "../components/ui/button"
import useSession from "@/app/hooks/use-session"



export default function Home() {

    const session = useSession()

    return (
        <div>
            {JSON.stringify(session)}
        </div>
    )
}
