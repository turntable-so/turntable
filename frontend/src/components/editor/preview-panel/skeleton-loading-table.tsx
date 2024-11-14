import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function SkeletonLoadingTable() {
  return (
    <div className="w-full flex items-center justify-center">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[100px]">
              <div className="animate-pulse h-4 bg-gray-200 rounded" />
            </TableHead>
            <TableHead>
              <div className="animate-pulse h-4 bg-gray-200 rounded" />
            </TableHead>
            <TableHead>
              <div className="animate-pulse h-4 bg-gray-200 rounded" />
            </TableHead>
            <TableHead className="text-right">
              <div className="animate-pulse h-4 bg-gray-200 rounded" />
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {Array.from({ length: 20 }).map((_, i) => (
            <TableRow key={i}>
              <TableCell className="">
                <div className="animate-pulse h-4 bg-gray-200 rounded" />
              </TableCell>
              <TableCell className="">
                <div className="animate-pulse h-4 bg-gray-200 rounded" />
              </TableCell>
              <TableCell className="">
                <div className="animate-pulse h-4 bg-gray-200 rounded" />
              </TableCell>
              <TableCell className="">
                <div className="animate-pulse h-4 bg-gray-200 rounded" />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
