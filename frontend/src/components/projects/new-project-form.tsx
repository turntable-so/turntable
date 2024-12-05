import { Button } from "@/components/ui/button";
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import type { UseFormReturn } from "react-hook-form";
import { toast } from "sonner";
import { createBranch, getBranches } from "../../app/actions/actions";
import type { ProjectFormValues } from "./types";

interface NewProjectFormProps {
  form: UseFormReturn<ProjectFormValues>;
  branches: string[];
  setBranches: (branches: string[]) => void;
}

export function NewProjectForm({
  form,
  branches,
  setBranches,
}: NewProjectFormProps) {
  const router = useRouter();
  const { isSubmitting } = form.formState;

  const handleProjectNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newProjectName = e.target.value;
    const transformedName = newProjectName
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");

    form.setValue("projectName", newProjectName);
    form.setValue("branchName", transformedName, { shouldValidate: false });
  };

  const onSubmit = async (values: ProjectFormValues) => {
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

  useEffect(() => {
    const fetchBranches = async () => {
      const result = await getBranches();
      setBranches(result.remote_branches);
      form.setValue("branchFrom", result.main_remote_branch);
    };
    fetchBranches();
  }, []);

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="projectName"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Project Name</FormLabel>
              <FormControl>
                <Input {...field} onChange={handleProjectNameChange} />
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
                This is the base git branch that the new branch will be created
                from
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
  );
}
