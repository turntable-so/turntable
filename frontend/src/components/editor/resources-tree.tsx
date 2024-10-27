import { Tree } from "@/components/ui/tree";
import { Folder, Workflow } from "lucide-react";
import { useState } from "react";
import useResizeObserver from "use-resize-observer";

export default function ResourcesTree() {
  const [treeData, setTreeData] = useState<any>([]);
  const { ref: treeRef, width, height } = useResizeObserver();

  return (
    <div ref={treeRef} className="flex flex-col h-full">
      <Tree
        height={height}
        width={width}
        data={treeData}
        initialSlelectedItemId="f12"
        onSelectChange={(item) => {
          if (item?.isSelectable) {
            if (context === "LINEAGE") {
              if (focusedAsset?.id !== item.id) {
                setIsLineageLoading(true);
                router.push(`/lineage/${item.id}`);
              }
            } else {
              fetchAssetPreview(item.id);
            }
          }
        }}
        folderIcon={Folder}
        itemIcon={Workflow}
      />
    </div>
  );
}
