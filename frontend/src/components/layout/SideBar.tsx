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
    return (
        <div className={cn(
            "flex-shrink-0",
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
                    <AccountSwitcher isCollapsed={isCollapsed} accounts={accounts} />
                </div>
                <Separator />
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
                            link: "/editor"
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


// export default function SideBar({ collapsed }: { collapsed: boolean }) {
//     const pathName = usePathname()

//     const { user, logout } = useSession()
//     const { current_workspace: workspace } = user


//     const [searchDialogOpen, setSearchDialogOpen] = useState(false)

//     useEffect(() => {
//         const down = (e: KeyboardEvent) => {
//             if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
//                 e.preventDefault()
//                 setSearchDialogOpen((open) => !open)
//             }
//         }

//         document.addEventListener("keydown", down)
//         return () => document.removeEventListener("keydown", down)
//     }, [])



//     const isCurrentTab = (path: string, tabPath: string) => {
//         if (tabPath === '/') {
//             if (path === '/') {
//                 return true
//             } else {
//                 return false
//             }
//         }

//         return path.startsWith(tabPath)
//     }


//     const MenuItems = [
//         { title: 'Connections', path: '/connections', Icon: () => <DatabaseZap className='size-5' /> },
//         { title: 'Assets', path: '/assets', Icon: () => <Boxes className='size-5' /> },
//         { title: 'Projects', path: '/editor', Icon: () => <Code className='size-5' /> },
//         { title: 'Lineage', path: '/lineage', Icon: () => <Network className='size-5' /> },
//         { title: 'Workspace', path: '/team', Icon: () => <Users className='size-5' /> },
//         { title: 'Settings', path: '/settings', Icon: () => <Settings className='size-5' /> },
//     ]

//     return (
//         <aside className={`${collapsed ? 'w-[75px]' : 'w-[350px]'} border-r max-w-[350px] bg-muted left-0 flex justify-center h-full `}>
//             <SearchDialog open={searchDialogOpen} setOpen={setSearchDialogOpen} />
//             {collapsed ? (
//                 <nav className="text-[15px] flex flex-col items-center space-y-4 mt-4">
//                     <Link href='/workspaces'>
//                         <div className='opacity-80 hover:opacity-100 text-ellipsis hover:cursor-pointer hover:bg-[#ebebeb] py-2 rounded-lg truncate  text-muted-foreground font flex items-center space-x-2 px-2'>
//                             <Avatar className='border h-8 w-8 flex items-center justify-center bg-gray-400 rounded-sm'>
//                                 <AvatarImage src={workspace.icon_url} />
//                                 <AvatarFallback className='text-white font-bold bg-gray-400'>{workspace.name.slice(0, 1).toUpperCase()}</AvatarFallback>
//                             </Avatar>
//                         </div>
//                     </Link>
//                     {/* <div className=' text-gray-400 font-medium'
//                         key={'Search'}>
//                         <Button onClick={() => setSearchDialogOpen(true)} variant='secondary' className='hover:bg-[#ebebeb] text-foreground-muted flex justify-center items-center'>
//                             <Search className='size-5' />

//                         </Button>
//                     </div> */}
//                     <div className='flex flex-col justify-between h-full'>
//                         <div className='space-y-4 py-2'>
//                             {MenuItems.map((tab: any) => (
//                                 <div className=''
//                                     key={tab.title}>
//                                     <Button

//                                         variant={isCurrentTab(pathName, tab.path) ? 'ghost' : 'ghost'}
//                                         size="icon"
//                                         className={`w-full rounded-lg ${isCurrentTab(pathName, tab.path) ? 'opacity-100' : 'opacity-50'} ${isCurrentTab(pathName, tab.path) ? 'bg-' : 'bg-transparent'} `}
//                                         aria-label={tab.title}
//                                     >
//                                         <Link href={tab.path} className="w-full">
//                                             <Button variant='secondary' className={`${isCurrentTab(pathName, tab.path) ? 'bg-[#ebebeb]' : 'hover:bg-[#ebebeb]'} px-4 p-2 rounded-lg w-full flex  space-x-2`}>
//                                                 <div className=''>
//                                                     <tab.Icon />
//                                                 </div>
//                                             </Button>
//                                         </Link>
//                                     </Button>
//                                 </div>

//                             ))}
//                         </div>
//                         {user && (
//                             <Popover>
//                                 <PopoverTrigger>
//                                     <div className='text-ellipsis hover:cursor-pointer hover:bg-[#ebebeb] py-2 rounded-lg truncate  text-muted-foreground font flex items-center space-x-2 mb-4 px-2'>
//                                         <Avatar className='size-8 border h-8 w8 flex items-center justify-center bg-gray-400'>
//                                             <AvatarImage src={user ? user.imageUrl : ''} />
//                                             <AvatarFallback className='bg-gray-400 text-white'>{user.email.slice(0, 1).toUpperCase()}</AvatarFallback>
//                                         </Avatar>
//                                     </div>
//                                 </PopoverTrigger>
//                                 <PopoverContent align="start" className='w-fit text-muted-foreground'>
//                                     <Button onClick={logout} variant='ghost' className='flex items-center'>
//                                         <LogOut className='h-4 w-4 mr-2' />
//                                         Sign out
//                                     </Button>
//                                 </PopoverContent>
//                             </Popover>
//                         )}
//                     </div>
//                 </nav>
//             ) : (
//                 <nav className="text-[15px] flex flex-col space-y-4 mt-4 p-0 px-6 mb-2   w-[275px]">
//                     <Link href='/workspaces'>
//                         <div className='opacity-80 hover:opacity-100 text-ellipsis hover:cursor-pointer hover:bg-[#ebebeb] py-2 rounded-lg truncate  text-muted-foreground font flex items-center space-x-2 px-2'>
//                             <div className='mr-1'>
//                                 <Avatar className='border h-8 w-8 flex items-center justify-center bg-gray-400 rounded-sm'>
//                                     <AvatarImage src={workspace.icon_url} />
//                                     <AvatarFallback className='text-white font-bold bg-gray-400'>{workspace.name.slice(0, 1).toUpperCase()}</AvatarFallback>
//                                 </Avatar>
//                             </div>
//                             <div className='text-lg truncate text-muted-foreground font-medium tracking-tight whitespace-nowrap'>{workspace.name}</div>
//                         </div>
//                     </Link>
//                     {/* <div className=' text-gray-400 font-medium' onClick={() => setSearchDialogOpen(true)}
//                         key={'Search'}>
//                         <div className="opacity-50 hover:opacity-100 cursor-pointer bg-white border border-gray-300 p-2 rounded-full w-full flex items-center justify-start space-x-2 px-4">
//                             <Search className='size-6 mr-2' />
//                             <div className='flex items-center justify-between w-full pr-1'>
//                                 <p className="">Search</p>
//                                 <p className="">⌘K</p>
//                             </div>
//                         </div>
//                     </div> */}
//                     <div className='flex flex-col justify-between h-full'>
//                         <div className='space-y-4 py-1'>
//                             {MenuItems.map((tab: any) => (
//                                 <div className=''
//                                     key={tab.title}>
//                                     <Button

//                                         variant={isCurrentTab(pathName, tab.path) ? 'ghost' : 'ghost'}
//                                         size="icon"
//                                         className={`w-full rounded-lg ${isCurrentTab(pathName, tab.path) ? 'opacity-100' : 'opacity-50'} ${isCurrentTab(pathName, tab.path) ? 'bg-' : 'bg-transparent'} `}
//                                         aria-label={tab.title}
//                                     >
//                                         <Link href={tab.path} className="w-full">
//                                             <div className={`${isCurrentTab(pathName, tab.path) ? 'bg-[#ebebeb]' : 'hover:bg-[#ebebeb]'} px-4 p-2 rounded-lg w-full flex  space-x-2`}>
//                                                 <div className='mr-2'>
//                                                     <tab.Icon />
//                                                 </div>
//                                                 <p className="font-normal text-[15px]">{tab.title}</p>
//                                             </div>
//                                         </Link>
//                                     </Button>
//                                 </div>

//                             ))}
//                         </div>
//                         {user && (
//                             <Popover>
//                                 <PopoverTrigger>
//                                     <div className='text-sm text-ellipsis hover:cursor-pointer hover:bg-[#ebebeb] py-2 rounded-lg truncate  text-muted-foreground font flex items-center space-x-2 mb-4 px-2'>
//                                         <div className='mr-1'>
//                                             <Avatar className='size-8 border h-8 w8 flex items-center justify-center bg-gray-400'>
//                                                 <AvatarImage src={user ? user.imageUrl : ''} />
//                                                 <AvatarFallback className='bg-gray-400 text-white'>{user.email.slice(0, 1).toUpperCase()}</AvatarFallback>
//                                             </Avatar>
//                                         </div>
//                                         <div>{user.email}</div>
//                                     </div>
//                                 </PopoverTrigger>
//                                 <PopoverContent align="start" className='w-fit text-muted-foreground'>
//                                     <Button onClick={logout} variant='ghost' className='flex items-center'>
//                                         <LogOut className='h-4 w-4 mr-2' />
//                                         Sign out
//                                     </Button>
//                                 </PopoverContent>
//                             </Popover>
//                         )}
//                     </div>
//                 </nav>

//             )
//             }

//         </aside >
//     )
// }