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
          <head>
            <link rel="icon" type="image/png" href="/favicon-96x96.png" sizes="96x96" />
            <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
            <link rel="shortcut icon" href="/favicon.ico" />
            <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
            <meta name="apple-mobile-web-app-title" content="Turntable" />
            <link rel="manifest" href="/site.webmanifest" />
          </head>
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
          <head>
            <link rel="icon" type="image/png" href="/favicon-96x96.png" sizes="96x96" />
            <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
            <link rel="shortcut icon" href="/favicon.ico" />
            <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
            <meta name="apple-mobile-web-app-title" content="Turntable" />
            <link rel="manifest" href="/site.webmanifest" />          </head>
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
