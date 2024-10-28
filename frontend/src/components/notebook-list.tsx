"use client";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatDistance, subDays } from "date-fns";
import { Notebook } from "lucide-react";
import { useRouter } from "next/navigation";

type Notebook = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

type TableProps = {
  notebooks: Notebook[];
};
export default function NotebookList({ notebooks }: TableProps) {
  const router = useRouter();

  return (
    <Table className="text-black">
      <TableHeader>
        <TableRow>
          <TableHead>Title</TableHead>
          <TableHead>Owner</TableHead>
          <TableHead>Created</TableHead>
          <TableHead>Your access</TableHead>
          <TableHead>Shared with</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {notebooks.map((notebook) => (
          <TableRow
            onClick={() => {
              router.push(`/notebooks/${notebook.id}`);
            }}
            key={notebook.id}
            className="hover:cursor-pointer"
          >
            <TableCell className="flex items-center">
              <Notebook className="h-4 w-4 mr-2" />
              <div className="font-medium">{notebook.title}</div>
            </TableCell>
            <TableCell className="">Ian Tracey</TableCell>
            <TableCell className="">
              {`${formatDistance(new Date(notebook.created_at), new Date())} ago`}
            </TableCell>
            <TableCell className="">Full access</TableCell>
            <TableCell className="">Everyone</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
