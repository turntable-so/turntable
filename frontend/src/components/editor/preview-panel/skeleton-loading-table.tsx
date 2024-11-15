import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function SkeletonLoadingTable() {
  const Loader = () => (
    <div className="animate-pulse h-4 bg-gray-200 dark:bg-zinc-800 rounded" />
  );
  return (
    <div className="w-full flex items-center justify-center">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[100px]">
              <Loader />
            </TableHead>
            <TableHead>
              <Loader />
            </TableHead>
            <TableHead>
              <Loader />
            </TableHead>
            <TableHead className="text-right">
              <Loader />
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {Array.from({ length: 20 }).map((_, i) => (
            <TableRow key={i}>
              <TableCell className="">
                <Loader />
              </TableCell>
              <TableCell className="">
                <Loader />
              </TableCell>
              <TableCell className="">
                <Loader />
              </TableCell>
              <TableCell className="">
                <Loader />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
