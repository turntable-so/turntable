"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { cn } from "@/lib/utils"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar"

interface AccountSwitcherProps {
    isCollapsed: boolean
    currentAccountId: string
    accounts: {
        id: string
        name: string
        icon_url: string
    }[]
}

export function AccountSwitcher({
    isCollapsed,
    accounts,
    currentAccountId
}: AccountSwitcherProps) {

    const router = useRouter()

    console.log({ accounts, currentAccountId })
    return (
        <Select defaultValue={currentAccountId} onValueChange={() => { }}>
            <SelectTrigger
                onClick={() => router.push('/workspaces')}
                className={cn(
                    "flex items-center gap-2 [&>span]:line-clamp-1 [&>span]:flex [&>span]:w-full [&>span]:items-center [&>span]:gap-1 [&>span]:truncate [&_svg]:h-4 [&_svg]:w-4 [&_svg]:shrink-0",
                    isCollapsed &&
                    "flex h-9 w-9 shrink-0 items-center justify-center p-0 [&>span]:w-auto [&>svg]:hidden"
                )}
                aria-label="Select account"
            >
                <SelectValue placeholder="Select an account">
                    {accounts.find((account) => account.id === currentAccountId)?.icon_url}
                    <Avatar className={`border ${isCollapsed ? 'h-8 w-8' : 'h-6 w-6'} flex items-center justify-center bg-gray-400 rounded-sm`}>
                        <AvatarImage src={accounts.find((account) => account.id === currentAccountId)?.icon_url} />
                        <AvatarFallback className='text-white font-bold bg-gray-400'>{accounts.find((account) => account.id === currentAccountId)?.name.slice(0, 1).toUpperCase()}</AvatarFallback>
                    </Avatar>
                    <span className={cn("ml-2", isCollapsed && "hidden")}>
                        {
                            accounts.find((account) => account.id === currentAccountId)
                                ?.name
                        }
                    </span>
                </SelectValue>
            </SelectTrigger>
        </Select>
    )
}
