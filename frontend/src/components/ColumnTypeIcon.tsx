import {
  Binary,
  Braces,
  Brackets,
  CalendarDays,
  Cuboid,
  Hash,
  IconNode,
  Type,
} from "lucide-react";

type ColumnType =
  | "string"
  | "numeric"
  | "float64"
  | "float32"
  | "boolean"
  | "date"
  | "timestamp"
  | "datetime"
  | "int64"
  | "int32"
  | "decimal"
  | "json"
  | "array";

export function ColumnTypeIcon({
  dataType,
  className,
}: { dataType: ColumnType; className: string }) {
  const iconsMap: Record<ColumnType, any> = {
    string: Type,
    numeric: Hash,
    float64: Hash,
    float32: Hash,
    boolean: Binary,
    date: CalendarDays,
    timestamp: CalendarDays,
    datetime: CalendarDays,
    int64: Hash,
    int32: Hash,
    decimal: Hash,
    json: Braces,
    array: Brackets,
  };

  if (!dataType) {
    return <Cuboid className={className} />;
  }

  const Icon = iconsMap[dataType.toLowerCase() as ColumnType];
  if (!Icon && dataType.toLowerCase().includes("timestamp")) {
    return <CalendarDays className={className} />;
  }
  if (!Icon) {
    return <Cuboid className={className} />;
  }

  return <Icon className={className} />;
}
