'use client'
import useSession from "@/app/hooks/use-session";
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { BookOpen, Boxes, Code, Database, DatabaseZap, FileBarChart, LogOut, Network, Settings, Users } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { SearchDialog } from '../SearchDialog';
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import { Separator } from "@/components/ui/separator"
import { Nav } from "@/components/nav"

import { cn } from "@/lib/utils"
import {
    AlertCircle,
    Archive,
    ArchiveX,
    File,
    Inbox,
    MessagesSquare,
    Search,
    Send,
    ShoppingCart,
    Trash2,
    Users2,
} from "lucide-react"
import { AccountSwitcher } from "../account-switcher";
import { TooltipProvider } from "../ui/tooltip";


export const accounts = [
    {
        label: "Alicia Koch",
        email: "alicia@example.com",
        icon: (
            <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <title>Vercel</title>
                <path d="M24 22.525H0l12-21.05 12 21.05z" fill="currentColor" />
            </svg>
        ),
    },
    {
        label: "Alicia Koch",
        email: "alicia@gmail.com",
        icon: (
            <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <title>Gmail</title>
                <path
                    d="M24 5.457v13.909c0 .904-.732 1.636-1.636 1.636h-3.819V11.73L12 16.64l-6.545-4.91v9.273H1.636A1.636 1.636 0 0 1 0 19.366V5.457c0-2.023 2.309-3.178 3.927-1.964L5.455 4.64 12 9.548l6.545-4.91 1.528-1.145C21.69 2.28 24 3.434 24 5.457z"
                    fill="currentColor"
                />
            </svg>
        ),
    },
    {
        label: "Alicia Koch",
        email: "alicia@me.com",
        icon: (
            <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <title>iCloud</title>
                <path
                    d="M13.762 4.29a6.51 6.51 0 0 0-5.669 3.332 3.571 3.571 0 0 0-1.558-.36 3.571 3.571 0 0 0-3.516 3A4.918 4.918 0 0 0 0 14.796a4.918 4.918 0 0 0 4.92 4.914 4.93 4.93 0 0 0 .617-.045h14.42c2.305-.272 4.041-2.258 4.043-4.589v-.009a4.594 4.594 0 0 0-3.727-4.508 6.51 6.51 0 0 0-6.511-6.27z"
                    fill="currentColor"
                />
            </svg>
        ),
    },
]
export default function SideBar({ isCollapsed }: { isCollapsed: boolean }) {
    const pathName = usePathname()
    const { user, logout } = useSession()
    const { current_workspace, workspaces } = user
    console.log({ user })
    return (
        <div className={cn(
            "flex-shrink-0 bg-muted",
            isCollapsed ? "w-[75px]" : "w-[250px]",
            "border-r"
        )}>
            <TooltipProvider delayDuration={0}>
                <div
                    className={cn(
                        "flex h-[52px] items-center justify-center",
                        isCollapsed ? "h-[52px]" : "px-2"
                    )}
                >
                    <AccountSwitcher currentAccountId={current_workspace.id} isCollapsed={isCollapsed} accounts={workspaces} />
                </div>
                <Separator />
                <div className='flex flex-col justify-between h-full mb-24'>
                    <Nav
                        isCollapsed={isCollapsed}
                        links={[
                            {
                                title: "Connections",
                                icon: DatabaseZap,
                                variant: pathName.startsWith("/connections") ? "secondary" : "ghost",
                                link: "/connections"
                            },
                            {
                                title: "Assets",
                                icon: Boxes,
                                variant: pathName.startsWith("/assets") ? "secondary" : "ghost",
                                link: "/assets"
                            },
                            {
                                title: "Projects",
                                icon: Code,
                                variant: pathName.startsWith("/editor") ? "secondary" : "ghost",
                                link: "/projects"
                            },
                            {
                                title: "Lineage",
                                icon: Network,
                                variant: pathName.startsWith("/lineage") ? "secondary" : "ghost",
                                link: "/lineage"
                            },
                            {
                                title: "Workspace",
                                icon: Users,
                                variant: pathName.startsWith("/team") ? "secondary" : "ghost",
                                link: "/team"
                            },
                            {
                                title: "Settings",
                                icon: Settings,
                                variant: pathName.startsWith("/settings") ? "secondary" : "ghost",
                                link: "/settings"
                            },
                        ]}
                    />
                    <div className="pb-20 w-full">
                        {user && (
                            <Popover>
                                <PopoverTrigger className='px-2 w-full'>
                                    <div className={`w-full px-2 py-2 text-sm text-ellipsis hover:cursor-pointer hover:bg-muted rounded-lg ${isCollapsed ? 'justify-center' : ''} truncate  text-muted-foreground font flex items-center space-x-2`}>
                                        <div className={isCollapsed ? 'mr-0' : 'mr-1'}>
                                            <Avatar className='size-8 border h-8 w8 flex items-center justify-center bg-gray-400'>
                                                <AvatarImage src={user ? user.imageUrl : ''} />
                                                <AvatarFallback className='bg-gray-400 text-white'>{user.email.slice(0, 1).toUpperCase()}</AvatarFallback>
                                            </Avatar>
                                        </div>
                                        {!isCollapsed && <div>{user.email}</div>}
                                    </div>
                                </PopoverTrigger>
                                <PopoverContent side="right" align="start" className='w-fit text-muted-foreground p-0'>
                                    <Button onClick={logout} variant='ghost' className='flex items-center'>
                                        <LogOut className='h-4 w-4 mr-2' />
                                        Sign out
                                    </Button>
                                </PopoverContent>
                            </Popover>
                        )}
                    </div>
                </div>
                {/* <Separator />
                <Nav
                    isCollapsed={isCollapsed}
                    links={[
                        {
                            title: "Social",
                            label: "972",
                            icon: Users2,
                            variant: "ghost",
                        },
                        {
                            title: "Updates",
                            label: "342",
                            icon: AlertCircle,
                            variant: "ghost",
                        },
                        {
                            title: "Forums",
                            label: "128",
                            icon: MessagesSquare,
                            variant: "ghost",
                        },
                        {
                            title: "Shopping",
                            label: "8",
                            icon: ShoppingCart,
                            variant: "ghost",
                        },
                        {
                            title: "Promotions",
                            label: "21",
                            icon: Archive,
                            variant: "ghost",
                        },
                    ]}
                /> */}
            </TooltipProvider>
        </div>
    )
}