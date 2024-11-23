"use client";

import { useFiles } from "@/app/contexts/FilesContext";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { DiffEditor } from "@monaco-editor/react";
import { useCallback, useEffect, useState } from "react";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Checkbox } from "../ui/checkbox";
import { toast } from "sonner";
import { GitMerge, Loader2, Undo2 } from "lucide-react";
import useSession from "@/app/hooks/use-session";
import { sync } from "@/app/actions/actions";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "../ui/tooltip";
interface BranchReviewDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const DiffView = ({
  original,
  modified,
}: {
  original: string;
  modified: string;
}) => (
  <DiffEditor
    text-muted-foreground
    original={original}
    modified={modified}
    language="sql"
    options={{
      minimap: { enabled: false },
      scrollbar: {
        vertical: "visible",
        horizontal: "visible",
        verticalScrollbarSize: 8,
        horizontalScrollbarSize: 8,
        verticalSliderSize: 8,
        horizontalSliderSize: 8,
      },
      lineNumbers: "on",
      wordWrap: "on",
      fontSize: 14,
      lineNumbersMinChars: 3,
    }}
    theme="mutedTheme"
  />
);

export default function BranchReviewDialog({
  open,
  onOpenChange,
}: BranchReviewDialogProps) {
  const handleOpenChange = useCallback(
    (open: boolean) => {
      onOpenChange(open);
    },
    [onOpenChange],
  );

  const [selectedChangeIndex, setSelectedChangeIndex] = useState<
    number | undefined
  >(undefined);

  const [selectedFilePaths, setSelectedFilePaths] = useState<string[]>([]);
  const [commitMessage, setCommitMessage] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  const {
    changes,
    schema,
    branchId,
    fetchChanges,
    commitChanges,
    pullRequestUrl,
    branchName,
    discardChanges,
    fetchFiles,
    sourceBranch,
  } = useFiles();
  const { user } = useSession();

  const hasChanges = !!(changes && changes.length > 0);

  useEffect(() => {
    if (branchId) {
      fetchChanges(branchId);
    }
  }, [open]);

  useEffect(() => {
    if (hasChanges) {
      setSelectedChangeIndex(0);
    }
  }, [changes]);

  const handleCheckboxChange = (checked: boolean, path: string) => {
    if (checked) {
      setSelectedFilePaths((prev) => [...prev, path]);
    } else {
      setSelectedFilePaths((prev) => prev.filter((p) => p !== path));
    }
  };

  const handleSubmit = async () => {
    if (selectedFilePaths.length === 0 || commitMessage.length === 0) {
      return;
    }
    setIsSubmitting(true);
    const success = await commitChanges(commitMessage, selectedFilePaths);
    if (success) {
      toast.success("Changes committed successfully");
    } else {
      toast.error("Failed to commit changes");
    }
    setIsSubmitting(false);
  };

  const handleSync = async () => {
    if (isSyncing) {
      return;
    }

    setIsSyncing(true);
    const response = await sync(branchId);
    if (response.error) {
      if (response.error === "MERGE_CONFLICT") {
        toast.error(
          "Merge conflict detected. Please resolve the conflict before syncing with remote.",
        );
      } else {
        toast.error("Something went wrong while syncing.");
      }
    } else {
      toast.success("Changes synced with remote successfully.");
      fetchFiles();
    }
    setIsSyncing(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="w-[96vw] h-[96vh] max-w-[96vw] max-h-[96vh]">
        <div className="flex gap-4  h-full">
          <div className="w-1/4  h-full justify-between flex-col flex">
            <div>
              <Button
                disabled={hasChanges}
                variant="secondary"
                className="w-full"
                size="sm"
                onClick={handleSync}
              >
                {isSyncing ? (
                  <div className="flex items-center">
                    <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                    Syncing with {sourceBranch}
                  </div>
                ) : (
                  <div className="flex items-center">
                    <GitMerge className="h-4 w-4 mr-1" />
                    <div>{`Sync with ${sourceBranch || "main"}`}</div>
                  </div>
                )}
              </Button>
              <>
                <div className="mt-4">
                  <label className="text-sm font-medium">Branch</label>
                  <div className="text-xs text-muted-foreground">
                    {branchName}
                  </div>
                </div>
                <div className="mt-4">
                  <label className="text-sm font-medium">Schema</label>
                  <div className="text-xs text-muted-foreground">{schema}</div>
                </div>
                <div className="mt-4">
                  <label className="text-sm font-medium">Commit message</label>
                  <textarea
                    value={commitMessage}
                    onChange={(e) => setCommitMessage(e.target.value)}
                    className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    placeholder="Latest changes on posthog-events"
                  />
                </div>
                <div className="mt-4">
                  <div className="flex items-center justify-between gap-2">
                    <label className="text-sm font-medium">Files changed</label>
                    <div className="flex items-center">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => {
                          if (
                            window.confirm(
                              "Are you sure you want to discard all changes?",
                            )
                          ) {
                            discardChanges(branchId);
                          }
                        }}
                      >
                        <Undo2 className="w-4 h-4 mr-1" />
                        Discard changes
                      </Button>
                    </div>
                  </div>
                  <div className="gap-1 flex flex-col overflow-y-scroll max-h-[300px]">
                    {(!changes || changes.length === 0) && (
                      <div className="text-xs text-muted-foreground">
                        No changes to commit
                      </div>
                    )}
                    {(changes || []).map((change: any, index: number) => (
                      <div
                        className={`truncate text-xs flex justify-between py-0.5 hover:bg-muted rounded-md hover:cursor-pointer ${selectedChangeIndex === index ? "bg-muted" : ""}`}
                        key={index}
                      >
                        <div className="flex items-center gap-2">
                          <Checkbox
                            checked={selectedFilePaths.includes(change.path)}
                            onCheckedChange={(checked) =>
                              handleCheckboxChange(
                                checked as boolean,
                                change.path,
                              )
                            }
                          />
                          <div onClick={() => setSelectedChangeIndex(index)}>
                            {change.path.split("/").pop()}
                          </div>
                        </div>
                        {change.type === "untracked" && (
                          <Badge variant="outline" className="text-green-500">
                            A
                          </Badge>
                        )}
                        {change.type === "modified" && (
                          <Badge variant="outline" className="text-blue-500">
                            M
                          </Badge>
                        )}
                        {change.type === "deleted" && (
                          <Badge variant="outline" className="text-red-500">
                            D
                          </Badge>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
                <div className="mt-4">
                  <label className="text-sm font-medium">
                    Create Pull Request
                  </label>
                  <div>
                    <a
                      href={pullRequestUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="text-blue-500 text-xs text-medium underline"
                    >
                      {pullRequestUrl}
                    </a>
                  </div>
                </div>
              </>
            </div>
            <div className="flex flex-col gap-4">
              <div className="text-xs text-muted-foreground">
                Committing as <b>{user?.email}</b>.<br />
              </div>
              <div className="flex gap-2 justify-end">
                <Button
                  variant="outline"
                  onClick={() => handleOpenChange(false)}
                >
                  Cancel
                </Button>
                {isSubmitting ? (
                  <Button disabled>
                    <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                    Committing
                  </Button>
                ) : (
                  <Button
                    disabled={
                      selectedFilePaths.length === 0 ||
                      commitMessage.length === 0
                    }
                    onClick={handleSubmit}
                  >
                    Commit
                  </Button>
                )}
              </div>
            </div>
          </div>

          <div className="pl-1 w-3/4">
            {selectedChangeIndex !== undefined &&
              changes?.[selectedChangeIndex] ? (
              <div className="h-[98%]">
                <div className="text-sm text-muted-foreground font-medium mb-2 text-center items-center">
                  {changes[selectedChangeIndex].path}
                </div>

                <DiffView
                  key={selectedChangeIndex}
                  original={changes?.[selectedChangeIndex].before}
                  modified={changes?.[selectedChangeIndex].after}
                />
              </div>
            ) : (
              <div className="m-2 text-xs text-muted-foreground bg-muted h-full flex-col flex-grow flex items-center justify-center">
                Select a file to see the diff
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
