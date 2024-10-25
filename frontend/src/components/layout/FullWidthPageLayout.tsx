"use client";

export default function FullWidthPageLayout({
  title,
  button,
  children,
  breadcrumbs,
}: {
  title?: string;
  children: React.ReactNode;
  button?: React.ReactNode;
  breadcrumbs?: string[];
}) {
  return (
    <div className="h-screen w-full flex flex-col max-w-7xl mt-16">
      <div className="px-8 pb-24">
        <div className="flex items-center justify-between ">
          <div className="text-3xl font-medium text-black">{title}</div>
          <div>{button}</div>
        </div>
        <div className="mt-8">{children}</div>
      </div>
    </div>
  );
}
