'use client'
import { Button } from "../ui/button"
import { Plus } from "lucide-react"

import CreateNotebookButton from "../../app/notebooks/CreateNotebookButton"
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "@radix-ui/react-dropdown-menu"
import { Breadcrumb, BreadcrumbList, BreadcrumbItem, BreadcrumbLink, BreadcrumbSeparator, BreadcrumbEllipsis, BreadcrumbPage } from "../ui/breadcrumb"

export default function FullWidthPageLayout({ title, button, children, breadcrumbs }: { title?: string, children: React.ReactNode, button?: React.ReactNode, breadcrumbs?: string[] }) {
    return (
        <div className='h-screen w-full flex flex-col max-w-[1000px]'>
            <div className='py-8 px-24'>

                <div className='flex items-center justify-between'>
                    <div className='text-4xl font-normal text-black'>{title}</div>
                    {button}
                </div>
            </div>
            <div className='px-24 pb-24'>
                {children}
            </div>
        </div >
    )
}