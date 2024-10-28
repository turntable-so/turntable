import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function ColumnsTable({
  columns,
}: {
  columns: {
    name: string;
    type: string;
    description: string;
    tests: string[];
    is_unused: boolean;
  }[];
}) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-[200px] text-wrap pl-4">Name</TableHead>
          <TableHead className="w-[150px] text-wrap">Data Type</TableHead>
          <TableHead>Description</TableHead>
          <TableHead>Tests</TableHead>
          <TableHead>Usage</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {columns
          .sort((a, b) => a.name.localeCompare(b.name))
          .map((column) => (
            <TableRow key={column.name} className="text-gray-500">
              <TableCell className="text-black font-medium pl-4">
                {column.name}
              </TableCell>
              <TableCell>{column.type}</TableCell>
              <TableCell className="pr-4">{column.description}</TableCell>
              <TableCell>
                {column.tests?.map((test) => (
                  <Badge variant="secondary" key={test}>
                    {test}
                  </Badge>
                ))}
              </TableCell>
              <TableCell>
                {column.is_unused && <Badge variant="outline">Unused</Badge>}
              </TableCell>
            </TableRow>
          ))}
      </TableBody>
    </Table>
  );
}
