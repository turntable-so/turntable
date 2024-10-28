import DataTable from "@/components/ui/data-table";
import type React from "react";

const ViewerContainer: React.FC = () => {
  return (
    <div className="p-8">
      <DataTable />
      <div className="h-12" />
    </div>
  );
};

export default ViewerContainer;
