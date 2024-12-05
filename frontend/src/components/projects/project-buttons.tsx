import { Button } from "@/components/ui/button";
import { zodResolver } from "@hookform/resolvers/zod";
import { Plus } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { NewProjectDialog } from "./new-project-dialog";
import { ProjectFilter } from "./project-filter";
import { type ProjectFormValues, projectFormSchema } from "./types";

export function ProjectButtons() {
  const form = useForm<ProjectFormValues>({
    resolver: zodResolver(projectFormSchema),
    defaultValues: {
      projectName: "",
      branchName: "",
      branchFrom: "",
      readOnly: false,
      schema: "",
    },
  });
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [branches, setBranches] = useState<string[]>([]);

  return (
    <div className="flex justify-between items-center gap-4">
      <ProjectFilter />
      <Button
        onClick={() => setIsDialogOpen(true)}
        className="rounded-full space-x-2"
      >
        <Plus className="size-4" />
        <div>New project</div>
      </Button>

      <NewProjectDialog
        isOpen={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        form={form}
        branches={branches}
        setBranches={setBranches}
      />
    </div>
  );
}
