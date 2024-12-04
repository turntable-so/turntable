"use client";
import { Card, CardContent, CardTitle } from "@/components/ui/card";
import NewWorkspaceButton from "@/components/workspaces/new-workspace-button";
import WorkspaceIcon from "@/components/workspaces/workspace-icon";
import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { getWorkspaces, switchWorkspace } from "../actions/actions";

type Workspace = {
  id: string;
  name: string;
  icon_url: string;
  icon_file: string;
  member_count: number;
};

export default function WorkspacePage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingWorkspaceId, setLoadingWorkspaceId] = useState<string | null>(
    null,
  );

  useEffect(() => {
    const fetchWorkspaces = async () => {
      setLoading(true);
      const workspaces = await getWorkspaces();
      setWorkspaces(workspaces);
      setLoading(false);
    };
    fetchWorkspaces();
  }, []);

  const handleSwitchWorkspace = async (workspaceId: string) => {
    setLoadingWorkspaceId(workspaceId);
    const workspace = await switchWorkspace(workspaceId);
    if (workspace.id) {
      window.location.href = "/connections";
    }
  };

  return (
    <div className="h-screen w-full flex items-center justify-center bg-muted">
      <Card className="w-[500px] max-h-[80vh] flex flex-col">
        <div className="flex justify-between items-center p-6">
          <CardTitle className="text-xl">Choose a Workspace</CardTitle>
          <NewWorkspaceButton />
        </div>
        <CardContent className="flex-1 overflow-y-auto">
          <div className="space-y-4">
            {loading ? (
              <div className="flex items-center justify-center">
                <Loader2 className="text-center h-6 w-6 animate-spin opacity-50" />
              </div>
            ) : (
              workspaces.map((workspace: Workspace) => (
                <div
                  className="flex justify-between items-center hover:bg-secondary dark:hover:bg-secondary p-4 rounded-md cursor-pointer"
                  key={workspace.id}
                  onClick={() => handleSwitchWorkspace(workspace.id)}
                >
                  <div className="flex items-center space-x-4">
                    <WorkspaceIcon
                      name={workspace.name}
                      iconUrl={workspace.icon_url || ""}
                    />
                    <div>
                      <p className="text-lg font-medium">{workspace.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {workspace.member_count}{" "}
                        {workspace.member_count === 1 ? "Member" : "Members"}
                      </p>
                    </div>
                  </div>
                  <div>
                    {loadingWorkspaceId === workspace.id && (
                      <Loader2 className="text-center h-6 w-6 animate-spin opacity-50" />
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
