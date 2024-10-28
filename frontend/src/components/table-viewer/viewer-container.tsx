import { getAssets } from "@/app/actions/actions";
import DataTable from "@/components/ui/data-table";
import type React from "react";
import { useEffect, useState } from "react";

const ViewerContainer: React.FC = () => {
  return (
    <div className="p-8">
      <DataTable />
      <div className="h-12" />
    </div>
  );
};

export default ViewerContainer;
