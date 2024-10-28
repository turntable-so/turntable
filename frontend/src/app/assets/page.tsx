"use client";
import ViewerContainer from "@/components/table-viewer/viewer-container";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AssetViewerProvider } from "@/contexts/AssetViewerContext";

export default function AssetsPage() {
  return (
    <AssetViewerProvider>
      <ScrollArea className="h-[calc(100vh-100px)]">
        <ViewerContainer />
      </ScrollArea>
    </AssetViewerProvider>
  );
}
