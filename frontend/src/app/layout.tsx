"use client";
import dynamic from "next/dynamic";
import { Inter as FontSans } from "next/font/google";
import { usePathname } from "next/navigation";
import { Fragment } from "react";
import { Toaster } from "sonner";
import { TooltipProvider } from "../components/ui/tooltip";
import { cn } from "../lib/utils";
import "./globals.css";
import AuthenticatedAppLayout from "./layout/authenticated-app-layout";
import { PHProvider } from "./providers";

const PostHogPageView = dynamic(() => import("./PostHogPageView"), {
  ssr: false,
});

const AnonPostHogPageView = dynamic(() => import("./AnonPostHogPageView"), {
  ssr: false,
});

const fontSans = FontSans({
  subsets: ["latin"],
  variable: "--font-sans",
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathName = usePathname();

  return (
    <Fragment>
      {/* eventually we want to remove this and do nested layouts */}
      {pathName.includes("/signin") ||
      pathName.includes("/signup") ||
      pathName.includes("/workspace") ? (
        <html lang="en" suppressHydrationWarning>
          <head />
          <PHProvider>
            <body
              className={cn(
                "min-h-screen bg-muted font-sans antialiased",
                fontSans.variable,
              )}
            >
              <AnonPostHogPageView />
              <div>{children}</div>
            </body>
          </PHProvider>
        </html>
      ) : (
        <html lang="en" suppressHydrationWarning>
          <head />
          <PHProvider>
            <body
              className={cn(
                "min-h-screen bg-muted font-sans antialiased",
                fontSans.variable,
              )}
            >
              <AuthenticatedAppLayout>
                <PostHogPageView />
                <TooltipProvider>{children}</TooltipProvider>
              </AuthenticatedAppLayout>
              <Toaster richColors />
            </body>
          </PHProvider>
        </html>
      )}
    </Fragment>
  );
}
