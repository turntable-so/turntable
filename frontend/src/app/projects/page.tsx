"use client";

import FullWidthPageLayout from "@/components/layout/FullWidthPageLayout";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { toast } from "sonner";

import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Plus } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { createBranch, getBranches, getProjects } from "../actions/actions";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const formSchema = z.object({
  projectName: z.string().min(2, {
    message: "Project name must be at least 2 characters.",
  }),
  branchName: z.string(),
  branchFrom: z.string().min(2, {
    message: "Branch name must be at least 2 characters.",
  }),
  readOnly: z.boolean().default(false),
  schema: z.string().min(2, {
    message: "Schema name must be at least 1 character.",
  }),
});

const NewProjectButton = () => {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      projectName: "",
      branchName: "",
      branchFrom: "",
      readOnly: false,
      schema: "",
    },
  });
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const router = useRouter();
  // Watch projectName to transform it for branchName
  const projectName = form.watch("projectName");
  const [branches, setBranches] = useState<string[]>([]);
  const { isSubmitting } = form.formState;

  useEffect(() => {
    const fetchBranches = async () => {
      const result = await getBranches();
      setBranches(result.remote_branches);
      form.setValue("branchFrom", result.main_remote_branch);
    };
    fetchBranches();
  }, []);

  // Update branchName whenever projectName changes
  useEffect(() => {
    const transformedName = projectName
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
    form.setValue("branchName", transformedName);
  }, [projectName, form]);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    const result = await createBranch(
      values.branchName,
      values.branchFrom,
      values.schema,
    );
    if (result.error) {
      toast.error(result.error);
    } else {
      router.push(`/editor/${result.id}`);
    }
  };

  return (
    <>
      <Button
        onClick={() => setIsDialogOpen(true)}
        className="rounded-full space-x-2"
      >
        <Plus className="size-4" />
        <div>New project</div>
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
                      A git branch in your repository will be created with this
                      name
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="branchName"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Branch Name</FormLabel>
                    <FormControl>
                      <Input {...field} disabled className="bg-muted" />
                    </FormControl>
                    <FormDescription>Created git branch name</FormDescription>
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
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a branch" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {branches.map((branch) => (
                          <SelectItem key={branch} value={branch}>
                            {branch}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      This is the base git branch that the new branch will be
                      created from
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="schema"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Schema</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormDescription>
                      The development schema to use for this project
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="flex justify-end">
                {isSubmitting ? (
                  <Button disabled className="flex items-center space-x-2">
                    <Loader2 className="size-4 animate-spin" />
                    <span>Creating</span>
                  </Button>
                ) : (
                  <Button type="submit">Create</Button>
                )}
              </div>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default function Projects() {
  const [projects, setProjects] = useState<[]>([]);

  const router = useRouter();

  useEffect(() => {
    const fetchProjects = async () => {
      const projects = await getProjects();
      setProjects(projects);
    };
    fetchProjects();
  }, []);

  return (
    <FullWidthPageLayout title="Projects" button={<NewProjectButton />}>
      <Table className="bg-white dark:bg-black rounded">
        <TableHeader>
          <TableRow>
            <TableHead className="p-4">Name</TableHead>
            <TableHead className="p-4">Created by</TableHead>
            <TableHead className="p-4">Created at</TableHead>
            <TableHead className="p-4">Branch</TableHead>
            <TableHead className="p-4">Your access</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {projects.map((project, i) => (
            <TableRow key={i}>
              <TableCell
                className="font-semibold hover:underline hover:cursor-pointer p-4"
                onClick={() => router.push(`/editor/${project.id}`)}
              >
                {project.name}
              </TableCell>
              <TableCell className="p-4">{project.created_by}</TableCell>
              <TableCell className="p-4">{project.created_at}</TableCell>
              <TableCell className="p-4">{project.branch_name}</TableCell>
              <TableCell className="p-4">
                {project.read_only ? "Read-only" : "Read/Write"}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </FullWidthPageLayout>
  );
}
