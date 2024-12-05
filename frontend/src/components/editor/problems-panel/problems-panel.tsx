import { useFiles } from "@/app/contexts/FilesContext";
import { Loader2 } from "lucide-react";

export default function ProblemsPanel() {
  const { problems, checkForProblemsOnEdit, isSqlFile } = useFiles();

  if (!isSqlFile) {
    return (
      <div className="flex items-center justify-center h-full">
        <p>Validation only runs on SQL files.</p>
      </div>
    );
  }

  return checkForProblemsOnEdit ? (
    problems.loading ? (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="animate-spin" />
      </div>
    ) : (
      <div className="p-4">
        {problems.data.length > 0 ? (
          problems.data.map((problem) => (
            <div key={problem.message}>{problem.message}</div>
          ))
        ) : (
          <div>No problems found</div>
        )}
      </div>
    )
  ) : (
    <div className="flex items-center justify-center h-full">
      <p>
        The settings "Check for problems on edit" is disabled. Please enable it
        to see problems.
      </p>
    </div>
  );
}
