"use client";

import { useFiles } from "@/app/contexts/FilesContext";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { DiffEditor } from "@monaco-editor/react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Checkbox } from "../ui/checkbox";
import { Switch } from "../ui/switch";
import { Tabs, TabsList, TabsTrigger } from "../ui/tabs";
import { toast } from "sonner";
import { ExternalLink, Loader2, Undo2 } from "lucide-react";
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

  const { changes, schema, branchId, fetchChanges, commitChanges, pullRequestUrl, branchName, isCloned, discardChanges, readOnly } = useFiles();

  useEffect(() => {
    if (branchId) {
      fetchChanges(branchId);
    }
  }, [open]);

  useEffect(() => {
    if (changes?.length > 0) {
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

  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="w-full max-w-[1700px] min-h-[900px]">
        <div className="flex gap-4  h-full">
          <div className="w-1/4  h-full justify-between flex-col flex">
            <div>
              <>
                <div className="mt-4">
                  <label className="text-sm font-medium">Branch</label>
                  <div className="text-xs text-muted-foreground">
                    {readOnly && "(Read Only) "}
                    {branchName}
                  </div>
                </div>
                <div className="mt-4">
                  <label className="text-sm font-medium">Schema</label>
                  <div className="text-xs text-muted-foreground">
                    {schema}
                  </div>
                </div>
                <div className="mt-4">
                  <label className="text-sm font-medium">Commit message</label>
                  <textarea
                    disabled={readOnly}
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
                          if (window.confirm('Are you sure you want to discard all changes?')) {
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
                            onCheckedChange={(checked) => handleCheckboxChange(checked as boolean, change.path)}
                          />
                          <div onClick={() => setSelectedChangeIndex(index)}>
                            {change.path}
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
                  <div className="mt-4">
                    <label className="text-sm font-medium">Create Pull Request</label>
                    <div>
                      <Button variant="link" asChild className="text-xs p-0 space-x-1">
                        <a href={pullRequestUrl} target="_blank" rel="noreferrer">
                          <div>
                            Open in Github
                          </div>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </Button>
                    </div>
                  </div>
                </div>
              </>
            </div>
            <div className="flex flex-col gap-4">
              <div className="text-xs text-muted-foreground">
                Committing as <b>root</b>.<br />
                <a
                  href="https://github.com/"
                  target="_blank"
                  className="text-black"
                  rel="noreferrer"
                >
                  Sign into Github
                </a>{" "}
                to use your account
              </div>
              <div className="flex gap-2 justify-end">
                <Button variant="outline" onClick={() => handleOpenChange(false)}>Cancel</Button>
                {isSubmitting ? (
                  <Button disabled>
                    <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                    Committing
                  </Button>
                ) : (
                  <Button disabled={readOnly || selectedFilePaths.length === 0 || commitMessage.length === 0} onClick={handleSubmit}>Commit</Button>
                )}
              </div>
            </div>
          </div>

          <div className="pl-1 w-3/4">
            {selectedChangeIndex !== undefined && changes?.[selectedChangeIndex] ? (
              <DiffView
                key={selectedChangeIndex}
                original={changes?.[selectedChangeIndex].before}
                modified={changes?.[selectedChangeIndex].after}
              />
            ) : (
              <div className="m-2 text-xs text-muted-foreground bg-muted h-full flex-col flex-grow flex items-center justify-center">
                Select a file to see the diff
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog >
  );
}
