import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { TableCell, TableRow } from "@/components/ui/table";
import { Ellipsis, Trash } from "lucide-react";
import { useRouter } from "next/navigation";
import type { Project } from "./types";

interface ProjectRowProps {
  project: Project;
}

export function ProjectRow({ project }: ProjectRowProps) {
  const router = useRouter();

  return (
    <TableRow key={project.id}>
      <TableCell
        className="font-semibold hover:underline hover:cursor-pointer p-4"
        onClick={() => router.push(`/editor/${project.id}`)}
      >
        {project.name}
      </TableCell>
      <TableCell className="p-2 text-sm">{project.branch_name}</TableCell>
      <TableCell className="p-2 text-sm">{project.schema}</TableCell>
      <TableCell className="p-2 text-sm">{project.schema}</TableCell>
      <TableCell className="p-2 text-sm">{project.created_at}</TableCell>
      <TableCell className="p-2 text-sm">
        {project.read_only ? "Read Only" : "Read/Write"}
      </TableCell>
      <TableCell className="p-2 text-sm">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <Ellipsis className="size-3" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" alignOffset={-5}>
            <DropdownMenuItem onClick={() => undefined}>
              <div className="flex items-center text-xs">
                <Trash className="mr-2 h-3 w-3" />
                Archive Project
              </div>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </TableCell>
    </TableRow>
  );
}
