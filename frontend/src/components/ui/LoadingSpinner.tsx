import { Loader2, type LucideIcon } from "lucide-react";
import React from "react";
import { Button, type ButtonProps } from "./button";

type LoaderButtonProps = ButtonProps & {
  isLoading?: boolean;
  icon?: LucideIcon;
  children: React.ReactNode;
  isDisabled?: boolean;
};

export const LoaderButton = React.forwardRef<
  HTMLButtonElement,
  LoaderButtonProps
>(
  (
    { onClick, isLoading, icon: Icon, children, isDisabled, variant, ...props },
    ref,
  ) => {
    if (isLoading) {
      return (
        <Button variant={variant} ref={ref} disabled={isLoading} {...props}>
          <Loader2 className="mr-2 h-4 w-4 animate-spin opacity-50" />
          {children}
        </Button>
      );
    }

    return (
      <Button
        {...props}
        variant={variant}
        onClick={onClick}
        ref={ref}
        disabled={isDisabled || isLoading}
      >
        {Icon ? (
          <>
            <Icon size={18} className="mr-3" />
            {children}
          </>
        ) : (
          children
        )}
      </Button>
    );
  },
);
LoaderButton.displayName = "LoaderButton";
