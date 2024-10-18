import React from "react";
import { type InputProps } from "@/components/ui/input";
import { cn } from "@/lib/utils";

const CommandInput = React.forwardRef<HTMLInputElement, InputProps>(
    ({ className, ...props }, ref) => {
      return (
        <div
          className={cn(
            "flex h-10 w-full items-center rounded-md border border-input bg-white pl-3 text-sm ring-offset-background focus-within:ring-1 focus-within:ring-ring focus-within:ring-offset-2",
            className,
          )}
        >
          <p className="text-muted-foreground font-semibold">dbt</p>
          <input
            {...props}
            ref={ref}
            className="w-full p-2 placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50"
          />
        </div>
      );
    },
  );

  export default CommandInput;