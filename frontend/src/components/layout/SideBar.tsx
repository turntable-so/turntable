'use client'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import getFeatureFlags from "../../lib/feature-flags";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import useSession from "@/app/hooks/use-session";
import { usePathname } from 'next/navigation';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button'
import { Database, SquarePen, Network, Users, Settings, Search, ChevronDown, LogOut, NotebookTabs } from 'lucide-react';
import { SearchDialog } from '../SearchDialog';




export default function SideBar({ collapsed }: { collapsed: boolean }) {
    const pathName = usePathname()

    const { user, logout } = useSession()
    const { current_workspace: workspace } = user


    const [searchDialogOpen, setSearchDialogOpen] = useState(false)

    useEffect(() => {
        const down = (e: KeyboardEvent) => {
            if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
                e.preventDefault()
                setSearchDialogOpen((open) => !open)
            }
        }

        document.addEventListener("keydown", down)
        return () => document.removeEventListener("keydown", down)
    }, [])



    const isCurrentTab = (path: string, tabPath: string) => {
        if (tabPath === '/') {
            if (path === '/') {
                return true
            } else {
                return false
            }
        }

        return path.startsWith(tabPath)
    }


    const MenuItems = true ? [
        { title: 'Sources', path: '/sources', Icon: () => <Database className='size-5' /> },
        { title: 'Projects', path: '/notebooks', Icon: () => <NotebookTabs className='size-5' /> },
        { title: 'Lineage', path: '/lineage', Icon: () => <Network className='size-5' /> },
        { title: 'Workspace', path: '/team', Icon: () => <Users className='size-5' /> },
        { title: 'Settings', path: '/settings', Icon: () => <Settings className='size-5' /> },
    ] : [
        { title: 'Sources', path: '/sources', Icon: () => <Database className='size-5' /> },
        { title: 'Lineage', path: '/lineage', Icon: () => <Network className='size-5' /> },
        { title: 'Workspace', path: '/team', Icon: () => <Users className='size-5' /> },
        { title: 'Settings', path: '/settings', Icon: () => <Settings className='size-5' /> },
    ]


    return (
        <aside className={`${collapsed ? 'w-[75px]' : 'w-[350px]'} border-r max-w-[350px] bg-muted left-0 flex justify-center h-full `}>
            <SearchDialog open={searchDialogOpen} setOpen={setSearchDialogOpen} />
            {collapsed ? (
                <nav className="text-[15px] flex flex-col items-center space-y-4 mt-4">
                    <Link href='/team'>
                        <div className='opacity-80 hover:opacity-100 text-ellipsis hover:cursor-pointer hover:bg-[#ebebeb] py-2 rounded-lg truncate  text-muted-foreground font flex items-center space-x-2 px-2'>
                            <Avatar className='border h-8 w-8 flex items-center justify-center bg-gray-400 rounded-sm'>
                                <AvatarImage src={workspace.icon_url} />
                                <AvatarFallback className='text-white font-bold bg-gray-400'>{workspace.name.slice(0, 1).toUpperCase()}</AvatarFallback>
                            </Avatar>
                        </div>
                    </Link>
                    <div className=' text-gray-400 font-medium'
                        key={'Search'}>
                        <Button onClick={() => setSearchDialogOpen(true)} variant='secondary' className='hover:bg-[#ebebeb] text-foreground-muted flex justify-center items-center'>
                            <Search className='size-5' />

                        </Button>
                    </div>
                    <div className='flex flex-col justify-between h-full'>
                        <div className='space-y-4 py-2'>
                            {MenuItems.map((tab: any) => (
                                <div className=''
                                    key={tab.title}>
                                    <Button

                                        variant={isCurrentTab(pathName, tab.path) ? 'ghost' : 'ghost'}
                                        size="icon"
                                        className={`w-full rounded-lg ${isCurrentTab(pathName, tab.path) ? 'opacity-100' : 'opacity-50'} ${isCurrentTab(pathName, tab.path) ? 'bg-' : 'bg-transparent'} `}
                                        aria-label={tab.title}
                                    >
                                        <Link href={tab.path} className="w-full">
                                            <Button variant='secondary' className={`${isCurrentTab(pathName, tab.path) ? 'bg-[#ebebeb]' : 'hover:bg-[#ebebeb]'} px-4 p-2 rounded-lg w-full flex  space-x-2`}>
                                                <div className=''>
                                                    <tab.Icon />
                                                </div>
                                            </Button>
                                        </Link>
                                    </Button>
                                </div>

                            ))}
                        </div>
                        {user && (
                            <Popover>
                                <PopoverTrigger>
                                    <div className='text-ellipsis hover:cursor-pointer hover:bg-[#ebebeb] py-2 rounded-lg truncate  text-muted-foreground font flex items-center space-x-2 mb-4 px-2'>
                                        <Avatar className='size-8 border h-8 w8 flex items-center justify-center bg-gray-400'>
                                            <AvatarImage src={user ? user.imageUrl : ''} />
                                            <AvatarFallback className='bg-gray-400 text-white'>{user.email.slice(0, 1).toUpperCase()}</AvatarFallback>
                                        </Avatar>
                                    </div>
                                </PopoverTrigger>
                                <PopoverContent align="start" className='w-fit text-muted-foreground'>
                                    <Button onClick={logout} variant='ghost' className='flex items-center'>
                                        <LogOut className='h-4 w-4 mr-2' />
                                        Sign out
                                    </Button>
                                </PopoverContent>
                            </Popover>
                        )}
                    </div>
                </nav>
            ) : (
                <nav className="text-[15px] flex flex-col space-y-4 mt-4 p-0 px-6 mb-2   w-[275px]">
                    <Link href='/team'>
                        <div className='opacity-80 hover:opacity-100 text-ellipsis hover:cursor-pointer hover:bg-[#ebebeb] py-2 rounded-lg truncate  text-muted-foreground font flex items-center space-x-2 px-2'>
                            <div className='mr-1'>
                                <Avatar className='border h-8 w-8 flex items-center justify-center bg-gray-400 rounded-sm'>
                                    <AvatarImage src={workspace.icon_url} />
                                    <AvatarFallback className='text-white font-bold bg-gray-400'>{workspace.name.slice(0, 1).toUpperCase()}</AvatarFallback>
                                </Avatar>
                            </div>
                            <div className='text-lg truncate text-muted-foreground font-medium tracking-tight whitespace-nowrap'>{workspace.name}</div>
                        </div>
                    </Link>
                    <div className=' text-gray-400 font-medium' onClick={() => setSearchDialogOpen(true)}
                        key={'Search'}>
                        <div className="opacity-50 hover:opacity-100 cursor-pointer bg-white border border-gray-300 p-2 rounded-full w-full flex items-center justify-start space-x-2 px-4">
                            <Search className='size-6 mr-2' />
                            <div className='flex items-center justify-between w-full pr-1'>
                                <p className="">Search</p>
                                <p className="">⌘K</p>
                            </div>
                        </div>
                    </div>
                    <div className='flex flex-col justify-between h-full'>
                        <div className='space-y-4 py-1'>
                            {MenuItems.map((tab: any) => (
                                <div className=''
                                    key={tab.title}>
                                    <Button

                                        variant={isCurrentTab(pathName, tab.path) ? 'ghost' : 'ghost'}
                                        size="icon"
                                        className={`w-full rounded-lg ${isCurrentTab(pathName, tab.path) ? 'opacity-100' : 'opacity-50'} ${isCurrentTab(pathName, tab.path) ? 'bg-' : 'bg-transparent'} `}
                                        aria-label={tab.title}
                                    >
                                        <Link href={tab.path} className="w-full">
                                            <div className={`${isCurrentTab(pathName, tab.path) ? 'bg-[#ebebeb]' : 'hover:bg-[#ebebeb]'} px-4 p-2 rounded-lg w-full flex  space-x-2`}>
                                                <div className='mr-2'>
                                                    <tab.Icon />
                                                </div>
                                                <p className="font-normal text-[15px]">{tab.title}</p>
                                            </div>
                                        </Link>
                                    </Button>
                                </div>

                            ))}
                        </div>
                        {user && (
                            <Popover>
                                <PopoverTrigger>
                                    <div className='text-sm text-ellipsis hover:cursor-pointer hover:bg-[#ebebeb] py-2 rounded-lg truncate  text-muted-foreground font flex items-center space-x-2 mb-4 px-2'>
                                        <div className='mr-1'>
                                            <Avatar className='size-8 border h-8 w8 flex items-center justify-center bg-gray-400'>
                                                <AvatarImage src={user ? user.imageUrl : ''} />
                                                <AvatarFallback className='bg-gray-400 text-white'>{user.email.slice(0, 1).toUpperCase()}</AvatarFallback>
                                            </Avatar>
                                        </div>
                                        <div>{user.email}</div>
                                    </div>
                                </PopoverTrigger>
                                <PopoverContent align="start" className='w-fit text-muted-foreground'>
                                    <Button onClick={logout} variant='ghost' className='flex items-center'>
                                        <LogOut className='h-4 w-4 mr-2' />
                                        Sign out
                                    </Button>
                                </PopoverContent>
                            </Popover>
                        )}
                    </div>
                </nav>

            )
            }

        </aside >
    )
}