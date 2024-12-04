import {
  Table,
  TableBody,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { LoadingRow } from "./loading-row";
import { ProjectRow } from "./project-row";
import type { Project } from "./types";

interface ProjectTableProps {
  projects: Project[];
  isLoading: boolean;
}

export function ProjectTable({ projects, isLoading }: ProjectTableProps) {
  return (
    <Table className="bg-white dark:bg-black rounded">
      <TableHeader>
        <TableRow>
          <TableHead className="p-2">Name</TableHead>
          <TableHead className="p-2">Owner</TableHead>
          <TableHead className="p-2">Created At</TableHead>
          <TableHead className="p-2">Git Branch</TableHead>
          <TableHead className="p-2">Schema</TableHead>
          <TableHead className="p-2">Your Access</TableHead>
          <TableHead className="p-2">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {isLoading ? (
          <LoadingRow />
        ) : (
          projects.map((project) => (
            <ProjectRow key={project.id} project={project} />
          ))
        )}
      </TableBody>
    </Table>
  );
}
