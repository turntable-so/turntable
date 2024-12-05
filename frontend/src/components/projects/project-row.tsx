import { archiveProject } from "@/app/actions/actions";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { TableCell, TableRow } from "@/components/ui/table";
import dayjs from "@/lib/dayjs";
import { Archive, Ellipsis } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import type { Project } from "./types";

interface ProjectRowProps {
  project: Project;
  fetchProjects: () => void;
  showActions: boolean;
}

export function ProjectRow({
  project,
  fetchProjects,
  showActions,
}: ProjectRowProps) {
  const router = useRouter();

  const handleArchive = async () => {
    const result = await archiveProject({ projectId: project.id });
    if (result.error) {
      toast.error(result.error);
      return;
    }
    toast.success("Project archived successfully.");
    fetchProjects();
  };

  return (
    <TableRow key={project.id}>
      <TableCell className="font-semibold hover:underline hover:cursor-pointer p-4">
        <Link href={`/editor/${project.id}`}>{project.name}</Link>
      </TableCell>
      <TableCell className="p-2 text-sm">{project.owner?.email}</TableCell>
      <TableCell className="p-2 text-sm">
        {dayjs(project.created_at).fromNow()}
      </TableCell>
      <TableCell className="p-2 text-sm">{project.branch_name}</TableCell>
      <TableCell className="p-2 text-sm">{project.schema}</TableCell>
      <TableCell className="p-2 text-sm">
        {project.read_only ? "Read Only" : "Read/Write"}
      </TableCell>
      {showActions && (
        <TableCell className="p-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <Ellipsis className="size-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" alignOffset={-5}>
              <DropdownMenuItem onClick={handleArchive}>
                <div className="flex items-center">
                  <Archive className="mr-2 h-4 w-4" />
                  Archive
                </div>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </TableCell>
      )}
    </TableRow>
  );
}
