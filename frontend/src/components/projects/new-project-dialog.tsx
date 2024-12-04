import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import type { UseFormReturn } from "react-hook-form";
import { NewProjectForm } from "./new-project-form";
import type { ProjectFormValues } from "./types";

interface NewProjectDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  form: UseFormReturn<ProjectFormValues>;
  branches: string[];
  setBranches: (branches: string[]) => void;
}

export function NewProjectDialog({
  isOpen,
  onOpenChange,
  form,
  branches,
  setBranches,
}: NewProjectDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogTitle>Create New Project</DialogTitle>
        <NewProjectForm
          form={form}
          branches={branches}
          setBranches={setBranches}
        />
      </DialogContent>
    </Dialog>
  );
}
