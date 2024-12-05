import { TableCell, TableRow } from "@/components/ui/table";

export function LoadingRow() {
  return (
    <TableRow>
      <TableCell className="font-semibold hover:underline hover:cursor-pointer p-4">
        <div className="h-4 w-full bg-muted rounded animate-pulse" />
      </TableCell>
      <TableCell className="p-2">
        <div className="h-4 w-full bg-muted rounded animate-pulse" />
      </TableCell>
      <TableCell className="p-2">
        <div className="h-4 w-full bg-muted rounded animate-pulse" />
      </TableCell>
      <TableCell className="p-2">
        <div className="h-4 w-full bg-muted rounded animate-pulse" />
      </TableCell>
      <TableCell className="p-2">
        <div className="h-4 w-full bg-muted rounded animate-pulse" />
      </TableCell>
      <TableCell className="p-2">
        <div className="h-4 w-full bg-muted rounded animate-pulse" />
      </TableCell>
      <TableCell className="p-2">
        <div className="h-4 w-full bg-muted rounded animate-pulse" />
      </TableCell>
    </TableRow>
  );
}
