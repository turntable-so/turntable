import { useFiles } from "@/app/contexts/FilesContext";
import { useLayoutContext } from "@/app/contexts/LayoutContext";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Sparkles } from "lucide-react";
import { useAISidebar } from "../ai/ai-sidebar-context";

export default function ProblemsBtnGroup() {
  const { problems, activeFile } = useFiles();
  const { sidebarRightShown, setSidebarRightShown } = useLayoutContext();
  const { setAiFileProblems, aiFileProblems} = useAISidebar();

  const showAddProblemsToChatButton =
    problems.data.length > 0 && !aiFileProblems;

  const addProblemsToChat = () => {
    setAiFileProblems({
      problems: problems.data.map((problem) => problem.message),
      file_name: activeFile?.node.name || "",
    });

    if (!sidebarRightShown) {
      setSidebarRightShown(true);
    }
  };

  return showAddProblemsToChatButton ? (
    <Tooltip delayDuration={0}>
      <TooltipTrigger asChild>
        <Button size="sm" variant="secondary" onClick={addProblemsToChat}>
          <Sparkles className="h-4 w-4 mr-2" />
        </Button>
      </TooltipTrigger>
      <TooltipContent>
        <p>Add to chat</p>
      </TooltipContent>
    </Tooltip>
  ) : null;
}
