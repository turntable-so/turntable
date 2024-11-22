import { cn } from "@/lib/utils";
import { CheckCircle2, CircleX, Loader2 } from "lucide-react";

type StatusIconProps = {
  status: "SUCCESS" | "FAILURE" | "STARTED";
  size?: "sm" | "lg";
};

export default function StatusIcon({ status, size = "sm" }: StatusIconProps) {
  const sizeClass = size === "sm" ? "h-4 w-4" : "h-6 w-6";
  const SuccessIcon = () => (
    <CheckCircle2 className={cn(sizeClass, "text-green-500")} />
  );
  const FailureIcon = () => (
    <CircleX className={cn(sizeClass, "text-red-500")} />
  );
  const StartedIcon = () => (
    <Loader2 className={cn(sizeClass, "animate-spin text-orange-500")} />
  );

  const StatusComponentMap = {
    SUCCESS: SuccessIcon,
    FAILURE: FailureIcon,
    STARTED: StartedIcon,
  };

  return StatusComponentMap[status]();
}
