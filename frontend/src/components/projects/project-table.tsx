import {
  Table,
  TableBody,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useSearchParams } from "next/dist/client/components/navigation";
import { LoadingRow } from "./loading-row";
import { ProjectRow } from "./project-row";
import type { FilterValue, Project } from "./types";

interface ProjectTableProps {
  projects: Project[];
  isLoading: boolean;
  fetchProjects: () => void;
}

export function ProjectTable({ projects, isLoading, fetchProjects }: ProjectTableProps) {
  const searchParams = useSearchParams();
  const filter = (searchParams.get("filter") || "active") as FilterValue;
  const showActions = filter !== "archived";

  return (
    <Table className="bg-white dark:bg-black rounded">
      <TableHeader>
        <TableRow>
          <TableHead className="p-2">Name</TableHead>
          <TableHead className="p-2">Owner</TableHead>
          <TableHead className="p-2">Created</TableHead>
          <TableHead className="p-2">Git Branch</TableHead>
          <TableHead className="p-2">Schema</TableHead>
          <TableHead className="p-2">Your Access</TableHead>
          {showActions && <TableHead className="p-2">Actions</TableHead>}
        </TableRow>
      </TableHeader>
      <TableBody>
        {isLoading ? (
          <>
            <LoadingRow />
            <LoadingRow />
            <LoadingRow />
          </>
        ) : (
          projects.map((project) => (
            <ProjectRow
              key={project.id}
              project={project}
              fetchProjects={fetchProjects}
              showActions={showActions}
            />
          ))
        )}
      </TableBody>
    </Table>
  );
}
