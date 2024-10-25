"use client";
import ViewerContainer from "@/components/table-viewer/viewer-container";
import { AssetViewerProvider } from "@/contexts/AssetViewerContext";

export default function AssetsPage() {
  return (
    <AssetViewerProvider>
      <ViewerContainer />
    </AssetViewerProvider>
  );
}
