import { z } from "zod";

export interface Project {
  id: string;
  name: string;
  branch_name: string;
  schema: string;
  created_at: string;
  read_only: boolean;
  archived: boolean;
  owner: {
    email: string;
  } | null;
}

export const projectFormSchema = z.object({
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

export type ProjectFormValues = z.infer<typeof projectFormSchema>;

export type FilterValue = "active" | "yours" | "archived";
