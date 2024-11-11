import { validateDbtQuery } from "@/app/actions/actions";
import { useFiles } from "@/app/contexts/FilesContext";
import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

export default function ProblemsPanel() {
  const { problems } = useFiles();

  return problems.loading ? (
    <div className="flex items-center justify-center h-full">
      <Loader2 className="animate-spin" />
    </div>
  ) : (
    <div className="p-4">
      {problems.data.map((problem) => (
        <div key={problem.message}>{problem.message}</div>
      ))}
    </div>
  );
}
