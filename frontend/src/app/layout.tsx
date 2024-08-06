'use client'
import { Inter } from "next/font/google";
import "./globals.css";
import { Inter as FontSans } from "next/font/google"
import { cn } from "../lib/utils";
import { usePathname } from "next/navigation";
import { Fragment, useEffect, useState } from "react";

import AuthenticatedAppLayout from "./layout/authenticated-app-layout";

const fontSans = FontSans({
  subsets: ["latin"],
  variable: "--font-sans",
})


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathName = usePathname()

  return (
    <Fragment>
      {/* eventually we want to remove this and do nested layouts */}
      {pathName.includes('/signin') || pathName.includes('/signup') || pathName.includes("/workspace") ? (
        <html lang="en" suppressHydrationWarning>
          <head />
          <body className={cn(
            "min-h-screen bg-muted font-sans antialiased",
            fontSans.variable
          )}>
            <div>
              {children}
            </div>
          </body>
        </html>
      ) : (
        <html lang="en" suppressHydrationWarning>
          <head />
          <body className={cn(
            "min-h-screen bg-background font-sans antialiased",
            fontSans.variable
          )}>
            <AuthenticatedAppLayout>
              {children}
            </AuthenticatedAppLayout>
          </body>
        </html>
      )}
    </Fragment>
  );
}
