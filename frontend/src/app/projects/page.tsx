'use client'
import FullWidthPageLayout from "@/components/layout/FullWidthPageLayout";
import { Button } from "@/components/ui/button";
import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableFooter,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Plus, Router } from "lucide-react";
import { useState } from 'react';
import { Dialog, DialogTrigger, DialogContent, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";

const formSchema = z.object({
    projectName: z.string().min(2, {
        message: "Project name must be at least 2 characters.",
    }),
    branchFrom: z.string().min(2, {
        message: "Branch name must be at least 2 characters.",
    }),
})


const NewProjectButton = () => {
    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            projectName: "",
            branchFrom: "main",
        },
    });
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const router = useRouter();

    const onSubmit = (values: z.infer<typeof formSchema>) => {
        router.push(`/editor`)
    }


    return (
        <>
            <Button onClick={() => setIsDialogOpen(true)} className='rounded-full space-x-2'>
                <Plus className='size-4' />
                <div>
                    New project
                </div>
            </Button>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogContent>
                    <DialogTitle>Create New Project</DialogTitle>
                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
                            <FormField
                                control={form.control}
                                name="projectName"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Project Name</FormLabel>
                                        <FormControl>
                                            <Input {...field} />
                                        </FormControl>
                                        <FormDescription>
                                            A git branch in your repository will be created with this name
                                        </FormDescription>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="branchFrom"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Base Git Branch</FormLabel>
                                        <FormControl>
                                            <Input  {...field} />
                                        </FormControl>
                                        <FormDescription>
                                            This is the base git branch that the new branch will be created from
                                        </FormDescription>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <div className="flex justify-end">
                                <Button type="submit">Create</Button>
                            </div>
                        </form>
                    </Form>
                </DialogContent>
            </Dialog>
        </>
    )
}

const projects = [
    {
        name: "marketing marts",
        createdBy: "Ian Tracey",
        createdAt: "2 hours ago",
        branch: "marketing-marts",
        access: "Full Access",
    },
    {
        name: "stg-ledger-investigation",
        createdBy: "Sami Kahil",
        createdAt: "3 days ago",
        branch: "stg-ledger-investigation",
        access: "Full Access",
    },
    {
        name: "sales_churn_q4",
        createdBy: "Justin Leder",
        createdAt: "1 day ago",
        branch: "sales-churn-q4",
        access: "Can View",
    },

]

export function TableDemo() {
    return (
        <Table className='bg-white rounded'>
            <TableHeader>
                <TableRow>
                    <TableHead className='p-4'>Name</TableHead>
                    <TableHead className='p-4'>Created by</TableHead>
                    <TableHead className='p-4'>Created at</TableHead>
                    <TableHead className='p-4'>Branch</TableHead>
                    <TableHead className='p-4'>Your access</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {projects.map((project) => (
                    <TableRow key={project.name}>
                        <TableCell className="font-semibold hover:underline hover:cursor-pointer p-4">{project.name}</TableCell>
                        <TableCell className='p-4'>{project.createdBy}</TableCell>
                        <TableCell className='p-4'>{project.createdAt}</TableCell>
                        <TableCell className="p-4">{project.branch}</TableCell>
                        <TableCell className="p-4">{project.access}</TableCell>
                    </TableRow>
                ))}
            </TableBody>
        </Table >
    )
}


export default function Projects() {
    return <FullWidthPageLayout title='Projects' button={<NewProjectButton />}>
        <TableDemo />
    </FullWidthPageLayout>
}

