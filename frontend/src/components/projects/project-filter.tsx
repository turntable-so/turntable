import type { FilterValue } from "@/components/projects/types";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useRouter, useSearchParams } from "next/navigation";

export function ProjectFilter() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const filter = (searchParams.get("filter") || "active") as FilterValue;

  const handleChange = (value: FilterValue) => {
    const params = new URLSearchParams(searchParams.toString());

    if (value === "active") {
      params.delete("filter");
    } else {
      params.set("filter", value);
    }

    router.push(`?${params.toString()}`);
  };

  return (
    <Select value={filter} onValueChange={handleChange}>
      <SelectTrigger>
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="active">Active Projects</SelectItem>
        <SelectItem value="yours">Your Projects</SelectItem>
        <SelectItem value="archived">Archived Projects</SelectItem>
      </SelectContent>
    </Select>
  );
}
