import { validateDbtQuery } from "@/app/actions/actions";
import { useFiles } from "@/app/contexts/FilesContext";
import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

type Problem = {
    message: string;
}

export default function ProblemsPanel() {
  const { debouncedActiveFileContent, branchId } = useFiles();
  const [loading, setLoading] = useState(false);
  const [problems, setProblems] = useState<Problem[]>([]);

  useEffect(() => {
    const validateQuery = async () => {
      if (debouncedActiveFileContent) {
        setLoading(true);
        const data = await validateDbtQuery({ query: debouncedActiveFileContent, branch_id: branchId });
        console.log("data returned", data);
        const formattedProblems = data.errors.map((error: any) => ({
          message: error.msg,
        }));
        setProblems(formattedProblems);
        setLoading(false);
      }
    };

    validateQuery();
  }, [debouncedActiveFileContent]);

  return loading ? <div className="flex items-center justify-center h-full"><Loader2 className="animate-spin" /></div> : <div>{problems.map((problem) => <div key={problem.message}>{problem.message}</div>)}</div>;
}
