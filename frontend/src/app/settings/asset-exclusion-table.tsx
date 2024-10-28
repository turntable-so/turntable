import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { AssetExclusionFilter, Settings } from "./types";

type AssetExclusionTableProps = {
  exclusionFilters: Settings["exclusion_filters"];
};

export function AssetExclusionTable({
  exclusionFilters,
}: AssetExclusionTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Substring name match</TableHead>
          <TableHead>Number of Assets Excluded</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {exclusionFilters.map((filter: AssetExclusionFilter) => (
          <TableRow key={filter.filter_name_contains}>
            <TableCell className="font-semibold">
              {filter.filter_name_contains}
            </TableCell>
            <TableCell>{filter.count}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
